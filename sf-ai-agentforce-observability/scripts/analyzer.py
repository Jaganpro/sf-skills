"""
Polars-based analysis helpers for STDM data.

Uses Polars lazy evaluation for memory-efficient analysis of
large datasets (100M+ rows).

Features:
- Session summary statistics
- Step distribution analysis
- Topic routing analysis
- Message timeline reconstruction
- All operations use lazy evaluation where possible

Usage:
    analyzer = STDMAnalyzer(Path("./stdm_data"))

    # Get session summary
    summary = analyzer.session_summary()
    print(summary)

    # Debug specific session
    timeline = analyzer.message_timeline("session_id")
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

import polars as pl
from rich.console import Console
from rich.table import Table


console = Console()


@dataclass
class STDMAnalyzer:
    """
    Polars-based analysis helpers for session tracing data.

    Uses lazy evaluation for memory efficiency, enabling analysis
    of datasets with millions of records.

    Attributes:
        data_dir: Directory containing extracted Parquet files

    Example:
        >>> analyzer = STDMAnalyzer(Path("./stdm_data"))
        >>> summary = analyzer.session_summary()
        >>> print(summary)
    """

    data_dir: Path

    def __post_init__(self):
        """Validate data directory exists."""
        self.data_dir = Path(self.data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

    def _get_parquet_path(self, entity: str) -> Path:
        """Get Parquet file path for entity."""
        # Try direct file first
        direct_path = self.data_dir / entity / "data.parquet"
        if direct_path.exists():
            return direct_path

        # Try partitioned directory
        partition_path = self.data_dir / entity
        if partition_path.exists() and partition_path.is_dir():
            # Check for parquet files
            parquet_files = list(partition_path.glob("**/*.parquet"))
            if parquet_files:
                return partition_path

        raise FileNotFoundError(f"No data found for {entity} in {self.data_dir}")

    def load_sessions(self) -> pl.LazyFrame:
        """
        Load sessions as lazy frame.

        Returns:
            Polars LazyFrame for sessions
        """
        path = self._get_parquet_path("sessions")
        return pl.scan_parquet(path)

    def load_interactions(self) -> pl.LazyFrame:
        """
        Load interactions as lazy frame.

        Returns:
            Polars LazyFrame for interactions
        """
        path = self._get_parquet_path("interactions")
        return pl.scan_parquet(path)

    def load_steps(self) -> pl.LazyFrame:
        """
        Load steps as lazy frame.

        Returns:
            Polars LazyFrame for steps
        """
        path = self._get_parquet_path("steps")
        return pl.scan_parquet(path)

    def load_messages(self) -> pl.LazyFrame:
        """
        Load messages as lazy frame.

        Returns:
            Polars LazyFrame for messages
        """
        path = self._get_parquet_path("messages")
        return pl.scan_parquet(path)

    def session_summary(self) -> pl.DataFrame:
        """
        Generate session summary statistics.

        Returns DataFrame with:
        - Total sessions by agent
        - Average turns per session
        - Average duration
        - End type distribution

        Returns:
            Polars DataFrame with summary statistics
        """
        sessions = self.load_sessions()
        interactions = self.load_interactions()

        # Calculate turns per session
        turns_per_session = (
            interactions
            .filter(pl.col("ssot__InteractionType__c") == "TURN")
            .group_by("ssot__aiAgentSessionId__c")
            .agg(pl.count().alias("turn_count"))
        )

        # Join with sessions and aggregate by agent
        summary = (
            sessions
            .join(
                turns_per_session,
                left_on="ssot__Id__c",
                right_on="ssot__aiAgentSessionId__c",
                how="left"
            )
            .group_by("ssot__AIAgentApiName__c")
            .agg([
                pl.count().alias("session_count"),
                pl.col("turn_count").mean().alias("avg_turns"),
                pl.col("ssot__AIAgentSessionEndType__c").filter(
                    pl.col("ssot__AIAgentSessionEndType__c") == "Completed"
                ).count().alias("completed_count"),
                pl.col("ssot__AIAgentSessionEndType__c").filter(
                    pl.col("ssot__AIAgentSessionEndType__c") == "Escalated"
                ).count().alias("escalated_count"),
                pl.col("ssot__AIAgentSessionEndType__c").filter(
                    pl.col("ssot__AIAgentSessionEndType__c") == "Abandoned"
                ).count().alias("abandoned_count"),
            ])
            .with_columns([
                (pl.col("completed_count") / pl.col("session_count") * 100).round(1).alias("completion_rate"),
            ])
            .sort("session_count", descending=True)
        )

        return summary.collect()

    def step_distribution(self, agent_name: Optional[str] = None) -> pl.DataFrame:
        """
        Analyze step type distribution.

        Returns:
        - LLM_STEP vs ACTION_STEP ratio
        - Most common action names
        - Average steps per turn

        Args:
            agent_name: Optional agent API name to filter

        Returns:
            Polars DataFrame with step distribution
        """
        steps = self.load_steps()
        interactions = self.load_interactions()

        if agent_name:
            sessions = self.load_sessions()
            session_ids = (
                sessions
                .filter(pl.col("ssot__AIAgentApiName__c") == agent_name)
                .select("ssot__Id__c")
            )
            interactions = interactions.join(
                session_ids,
                left_on="ssot__aiAgentSessionId__c",
                right_on="ssot__Id__c",
                how="inner"
            )
            interaction_ids = interactions.select("ssot__Id__c")
            steps = steps.join(
                interaction_ids,
                left_on="ssot__AIAgentInteractionId__c",
                right_on="ssot__Id__c",
                how="inner"
            )

        # Step type distribution
        step_types = (
            steps
            .group_by("ssot__AIAgentInteractionStepType__c")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
        )

        return step_types.collect()

    def action_distribution(self, agent_name: Optional[str] = None) -> pl.DataFrame:
        """
        Analyze action name distribution for ACTION_STEP types.

        Args:
            agent_name: Optional agent API name to filter

        Returns:
            Polars DataFrame with action counts
        """
        steps = self.load_steps()

        # Filter to action steps only
        action_steps = steps.filter(
            pl.col("ssot__AIAgentInteractionStepType__c") == "ACTION_STEP"
        )

        if agent_name:
            sessions = self.load_sessions()
            interactions = self.load_interactions()

            session_ids = (
                sessions
                .filter(pl.col("ssot__AIAgentApiName__c") == agent_name)
                .select("ssot__Id__c")
            )
            interaction_ids = (
                interactions
                .join(
                    session_ids,
                    left_on="ssot__aiAgentSessionId__c",
                    right_on="ssot__Id__c",
                    how="inner"
                )
                .select(pl.col("ssot__Id__c").alias("interaction_id"))
            )
            action_steps = action_steps.join(
                interaction_ids,
                left_on="ssot__AIAgentInteractionId__c",
                right_on="interaction_id",
                how="inner"
            )

        # Group by action name
        actions = (
            action_steps
            .group_by("ssot__Name__c")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
        )

        return actions.collect()

    def topic_analysis(self) -> pl.DataFrame:
        """
        Analyze topic routing patterns.

        Returns:
        - Topic frequency
        - Sessions per topic
        - Average turns per topic

        Returns:
            Polars DataFrame with topic analysis
        """
        interactions = self.load_interactions()

        # Filter to TURN interactions (not SESSION_END)
        turns = interactions.filter(
            pl.col("ssot__InteractionType__c") == "TURN"
        )

        # Topic frequency
        topics = (
            turns
            .group_by("ssot__TopicApiName__c")
            .agg([
                pl.count().alias("turn_count"),
                pl.col("ssot__aiAgentSessionId__c").n_unique().alias("session_count"),
            ])
            .with_columns([
                (pl.col("turn_count") / pl.col("session_count")).round(2).alias("avg_turns_per_session"),
            ])
            .sort("turn_count", descending=True)
        )

        return topics.collect()

    def message_timeline(self, session_id: str) -> pl.DataFrame:
        """
        Reconstruct message timeline for a specific session.

        Useful for debugging agent behavior by seeing the full
        conversation flow.

        Args:
            session_id: Session ID to analyze

        Returns:
            Polars DataFrame with chronological messages
        """
        sessions = self.load_sessions()
        interactions = self.load_interactions()
        messages = self.load_messages()
        steps = self.load_steps()

        # Get session info
        session_info = (
            sessions
            .filter(pl.col("ssot__Id__c") == session_id)
            .collect()
        )

        if session_info.is_empty():
            raise ValueError(f"Session not found: {session_id}")

        # Get interactions for this session
        session_interactions = (
            interactions
            .filter(pl.col("ssot__aiAgentSessionId__c") == session_id)
            .select("ssot__Id__c")
        )

        # Get messages
        session_messages = (
            messages
            .join(
                session_interactions,
                left_on="ssot__AIAgentInteractionId__c",
                right_on="ssot__Id__c",
                how="inner"
            )
            .select([
                "ssot__MessageSentTimestamp__c",
                "ssot__AIAgentInteractionMessageType__c",
                "ssot__ContentText__c",
                "ssot__AIAgentInteractionId__c",
            ])
            .with_columns([
                pl.lit("MESSAGE").alias("event_type"),
            ])
        )

        # Get steps
        session_steps = (
            steps
            .join(
                session_interactions,
                left_on="ssot__AIAgentInteractionId__c",
                right_on="ssot__Id__c",
                how="inner"
            )
            .select([
                pl.lit(None).cast(pl.Utf8).alias("ssot__MessageSentTimestamp__c"),
                pl.col("ssot__AIAgentInteractionStepType__c").alias("ssot__AIAgentInteractionMessageType__c"),
                pl.col("ssot__Name__c").alias("ssot__ContentText__c"),
                "ssot__AIAgentInteractionId__c",
            ])
            .with_columns([
                pl.lit("STEP").alias("event_type"),
            ])
        )

        # Combine and sort
        timeline = (
            pl.concat([session_messages, session_steps])
            .sort("ssot__MessageSentTimestamp__c")
        )

        return timeline.collect()

    def end_type_distribution(self) -> pl.DataFrame:
        """
        Analyze session end type distribution.

        Returns:
            Polars DataFrame with end type counts and percentages
        """
        sessions = self.load_sessions()

        distribution = (
            sessions
            .group_by("ssot__AIAgentSessionEndType__c")
            .agg(pl.count().alias("count"))
            .with_columns([
                (pl.col("count") / pl.col("count").sum() * 100).round(1).alias("percentage"),
            ])
            .sort("count", descending=True)
        )

        return distribution.collect()

    def sessions_by_date(self) -> pl.DataFrame:
        """
        Get session counts by date.

        Returns:
            Polars DataFrame with daily session counts
        """
        sessions = self.load_sessions()

        daily = (
            sessions
            .with_columns([
                pl.col("ssot__StartTimestamp__c").str.slice(0, 10).alias("date"),
            ])
            .group_by("date")
            .agg(pl.count().alias("session_count"))
            .sort("date")
        )

        return daily.collect()

    def find_failed_sessions(self) -> pl.DataFrame:
        """
        Find sessions that ended with failures or escalations.

        Returns:
            Polars DataFrame with failed/escalated sessions
        """
        sessions = self.load_sessions()

        failed = (
            sessions
            .filter(
                pl.col("ssot__AIAgentSessionEndType__c").is_in(["Escalated", "Abandoned", "Failed"])
            )
            .sort("ssot__StartTimestamp__c", descending=True)
        )

        return failed.collect()

    def print_summary(self):
        """Print comprehensive summary to console."""
        console.print("\n[bold cyan]📊 SESSION TRACING SUMMARY[/bold cyan]")
        console.print("═" * 60)

        # Session summary
        try:
            summary = self.session_summary()
            console.print("\n[bold]Sessions by Agent[/bold]")

            table = Table()
            table.add_column("Agent", style="cyan")
            table.add_column("Sessions", justify="right")
            table.add_column("Avg Turns", justify="right")
            table.add_column("Completion %", justify="right")

            for row in summary.iter_rows(named=True):
                table.add_row(
                    str(row.get("ssot__AIAgentApiName__c", "Unknown")),
                    str(row.get("session_count", 0)),
                    f"{row.get('avg_turns', 0):.1f}",
                    f"{row.get('completion_rate', 0):.1f}%",
                )

            console.print(table)
        except Exception as e:
            console.print(f"[yellow]Could not load session summary: {e}[/yellow]")

        # End type distribution
        try:
            end_types = self.end_type_distribution()
            console.print("\n[bold]End Type Distribution[/bold]")

            for row in end_types.iter_rows(named=True):
                end_type = row.get("ssot__AIAgentSessionEndType__c", "Unknown")
                count = row.get("count", 0)
                pct = row.get("percentage", 0)

                icon = "✅" if end_type == "Completed" else "🔄" if end_type == "Escalated" else "❌"
                console.print(f"  {icon} {end_type}: {count} ({pct}%)")
        except Exception as e:
            console.print(f"[yellow]Could not load end type distribution: {e}[/yellow]")

        # Topic analysis
        try:
            topics = self.topic_analysis()
            console.print("\n[bold]Top Topics[/bold]")

            for i, row in enumerate(topics.head(5).iter_rows(named=True)):
                topic = row.get("ssot__TopicApiName__c", "Unknown")
                count = row.get("turn_count", 0)
                console.print(f"  {i+1}. {topic}: {count} turns")
        except Exception as e:
            console.print(f"[yellow]Could not load topic analysis: {e}[/yellow]")

    def print_session_debug(self, session_id: str):
        """Print detailed debug view for a session."""
        console.print(f"\n[bold cyan]🔍 SESSION DEBUG: {session_id}[/bold cyan]")
        console.print("═" * 60)

        try:
            # Get session info
            sessions = self.load_sessions()
            session = (
                sessions
                .filter(pl.col("ssot__Id__c") == session_id)
                .collect()
            )

            if session.is_empty():
                console.print(f"[red]Session not found: {session_id}[/red]")
                return

            row = session.row(0, named=True)
            console.print(f"\nAgent: [cyan]{row.get('ssot__AIAgentApiName__c', 'Unknown')}[/cyan]")
            console.print(f"Started: {row.get('ssot__StartTimestamp__c', 'N/A')}")
            console.print(f"Ended: {row.get('ssot__EndTimestamp__c', 'N/A')}")
            console.print(f"End Type: {row.get('ssot__AIAgentSessionEndType__c', 'N/A')}")

            # Get timeline
            timeline = self.message_timeline(session_id)

            console.print("\n[bold]Timeline[/bold]")
            console.print("─" * 60)

            for event in timeline.iter_rows(named=True):
                timestamp = event.get("ssot__MessageSentTimestamp__c", "")
                event_type = event.get("event_type", "")
                msg_type = event.get("ssot__AIAgentInteractionMessageType__c", "")
                content = event.get("ssot__ContentText__c", "")

                if event_type == "MESSAGE":
                    icon = "→" if msg_type == "INPUT" else "←"
                    style = "green" if msg_type == "INPUT" else "blue"
                    label = "[INPUT]" if msg_type == "INPUT" else "[OUTPUT]"
                else:
                    icon = "⚡"
                    style = "yellow"
                    label = f"[{msg_type}]"

                # Truncate long content
                if content and len(content) > 80:
                    content = content[:77] + "..."

                time_str = timestamp[:19] if timestamp else "        "
                console.print(f"{time_str} │ [{style}]{label}[/{style}] {content}")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
