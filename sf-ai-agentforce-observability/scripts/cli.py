#!/usr/bin/env python3
"""
CLI for Agentforce Session Tracing extraction and analysis.

Entry point for the stdm-extract command.

Usage:
    python3 scripts/cli.py extract --org prod --days 7 --output ./data
    python3 scripts/cli.py analyze --data-dir ./data
    python3 scripts/cli.py debug-session --data-dir ./data --session-id "a0x..."

Commands:
    extract             Extract session data from Data Cloud
    extract-tree        Extract complete tree for specific sessions
    extract-incremental Continue from last extraction watermark
    analyze             Generate summary statistics
    debug-session       Show detailed session timeline
    topics              Show topic routing analysis
    count               Count records in Data Cloud
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


def get_auth(org_alias: str, consumer_key: Optional[str] = None):
    """Get authentication for the specified org."""
    from scripts.auth import DataCloudAuth, get_auth_from_env

    if consumer_key:
        return DataCloudAuth(org_alias=org_alias, consumer_key=consumer_key)

    # Try environment variable
    try:
        return get_auth_from_env(org_alias)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("\nTo configure authentication:")
        console.print("  1. Set SF_CONSUMER_KEY environment variable")
        console.print(f"  2. Or set SF_{org_alias.upper()}_CONSUMER_KEY")
        console.print("  3. Or pass --consumer-key argument")
        raise click.Abort()


@click.group()
@click.version_option(version="1.0.0", prog_name="stdm-extract")
def cli():
    """
    Agentforce Session Tracing extraction tool.

    Extract and analyze agent session data from Salesforce Data Cloud.
    """
    pass


@cli.command()
@click.option("--org", required=True, help="Salesforce org alias")
@click.option("--consumer-key", help="Connected App consumer key")
@click.option("--days", default=7, help="Extract last N days (default: 7)")
@click.option("--since", type=click.DateTime(), help="Start date (YYYY-MM-DD)")
@click.option("--until", type=click.DateTime(), help="End date (YYYY-MM-DD)")
@click.option("--agent", multiple=True, help="Filter by agent API name (repeatable)")
@click.option("--output", type=click.Path(), default="./stdm_data", help="Output directory")
@click.option("--no-children", is_flag=True, help="Skip extracting child records")
@click.option("--verbose", is_flag=True, help="Show detailed progress")
def extract(
    org: str,
    consumer_key: Optional[str],
    days: int,
    since: Optional[datetime],
    until: Optional[datetime],
    agent: tuple,
    output: str,
    no_children: bool,
    verbose: bool,
):
    """
    Extract session tracing data from Data Cloud.

    Extracts sessions and optionally all child records (interactions,
    steps, messages) for the specified time range.

    Examples:

        # Last 7 days
        stdm-extract extract --org prod --days 7

        # Specific date range
        stdm-extract extract --org prod --since 2026-01-01 --until 2026-01-15

        # Filter by agent
        stdm-extract extract --org prod --agent Customer_Support_Agent
    """
    from scripts.auth import DataCloudAuth
    from scripts.datacloud_client import DataCloudClient
    from scripts.extractor import STDMExtractor

    # Determine date range
    if since:
        start_date = since
    else:
        start_date = datetime.utcnow() - timedelta(days=days)

    end_date = until or datetime.utcnow()

    # Get authentication
    auth = get_auth(org, consumer_key)

    console.print(f"\n[bold cyan]📊 STDM Extraction[/bold cyan]")
    console.print(f"Org: [cyan]{org}[/cyan]")
    console.print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    if agent:
        console.print(f"Agents: {', '.join(agent)}")
    console.print(f"Output: {output}")
    console.print("")

    try:
        # Test connection
        console.print("[dim]Testing connection...[/dim]")
        auth.test_connection()
        console.print("[green]✓ Connected to Data Cloud[/green]\n")

        # Create client and extractor
        client = DataCloudClient(auth)
        extractor = STDMExtractor(client, Path(output))

        # Run extraction
        result = extractor.extract_sessions(
            since=start_date,
            until=end_date,
            agent_names=list(agent) if agent else None,
            include_children=not no_children,
            show_progress=True,
        )

        # Print summary
        console.print("")
        extractor.print_summary(result)

        if result.errors:
            sys.exit(1)

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command("extract-tree")
@click.option("--org", required=True, help="Salesforce org alias")
@click.option("--consumer-key", help="Connected App consumer key")
@click.option("--session-id", required=True, multiple=True, help="Session ID(s) to extract")
@click.option("--output", type=click.Path(), default="./stdm_debug", help="Output directory")
@click.option("--verbose", is_flag=True, help="Show detailed progress")
def extract_tree(
    org: str,
    consumer_key: Optional[str],
    session_id: tuple,
    output: str,
    verbose: bool,
):
    """
    Extract complete session tree for specific session IDs.

    Extracts all related records (interactions, steps, messages) for
    the specified sessions. Useful for debugging specific conversations.

    Examples:

        # Single session
        stdm-extract extract-tree --org prod --session-id "a0x..."

        # Multiple sessions
        stdm-extract extract-tree --org prod --session-id "a0x..." --session-id "a0y..."
    """
    from scripts.datacloud_client import DataCloudClient
    from scripts.extractor import STDMExtractor

    auth = get_auth(org, consumer_key)

    console.print(f"\n[bold cyan]📊 Session Tree Extraction[/bold cyan]")
    console.print(f"Sessions: {len(session_id)}")
    console.print(f"Output: {output}")
    console.print("")

    try:
        client = DataCloudClient(auth)
        extractor = STDMExtractor(client, Path(output))

        result = extractor.extract_session_tree(
            session_ids=list(session_id),
            show_progress=True,
        )

        console.print("")
        extractor.print_summary(result)

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command("extract-incremental")
@click.option("--org", required=True, help="Salesforce org alias")
@click.option("--consumer-key", help="Connected App consumer key")
@click.option("--agent", multiple=True, help="Filter by agent API name")
@click.option("--output", type=click.Path(), default="./stdm_data", help="Output directory")
@click.option("--verbose", is_flag=True, help="Show detailed progress")
def extract_incremental(
    org: str,
    consumer_key: Optional[str],
    agent: tuple,
    output: str,
    verbose: bool,
):
    """
    Continue extraction from last watermark.

    Reads the watermark file from previous extraction and extracts
    only new data. If no watermark exists, extracts last 24 hours.

    Examples:

        stdm-extract extract-incremental --org prod --output ./stdm_data
    """
    from scripts.datacloud_client import DataCloudClient
    from scripts.extractor import STDMExtractor

    auth = get_auth(org, consumer_key)

    console.print(f"\n[bold cyan]📊 Incremental Extraction[/bold cyan]")
    console.print(f"Output: {output}")
    console.print("")

    try:
        client = DataCloudClient(auth)
        extractor = STDMExtractor(client, Path(output))

        result = extractor.extract_incremental(
            agent_names=list(agent) if agent else None,
            show_progress=True,
        )

        console.print("")
        extractor.print_summary(result)

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option("--data-dir", type=click.Path(exists=True), required=True, help="Data directory")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "csv"]), default="table")
def analyze(data_dir: str, output_format: str):
    """
    Generate summary statistics from extracted data.

    Analyzes sessions, interactions, steps, and messages to provide
    overview statistics.

    Examples:

        stdm-extract analyze --data-dir ./stdm_data
        stdm-extract analyze --data-dir ./stdm_data --format json
    """
    from scripts.analyzer import STDMAnalyzer

    try:
        analyzer = STDMAnalyzer(Path(data_dir))

        if output_format == "table":
            analyzer.print_summary()
        elif output_format == "json":
            import json
            summary = analyzer.session_summary()
            console.print(json.dumps(summary.to_dicts(), indent=2))
        elif output_format == "csv":
            summary = analyzer.session_summary()
            console.print(summary.write_csv())

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command("debug-session")
@click.option("--data-dir", type=click.Path(exists=True), required=True, help="Data directory")
@click.option("--session-id", required=True, help="Session ID to debug")
def debug_session(data_dir: str, session_id: str):
    """
    Show detailed timeline for a specific session.

    Reconstructs the conversation flow with all messages and steps
    in chronological order.

    Examples:

        stdm-extract debug-session --data-dir ./stdm_data --session-id "a0x..."
    """
    from scripts.analyzer import STDMAnalyzer

    try:
        analyzer = STDMAnalyzer(Path(data_dir))
        analyzer.print_session_debug(session_id)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--data-dir", type=click.Path(exists=True), required=True, help="Data directory")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "csv"]), default="table")
def topics(data_dir: str, output_format: str):
    """
    Show topic routing analysis.

    Analyzes which topics are handling conversations and how often.

    Examples:

        stdm-extract topics --data-dir ./stdm_data
    """
    from scripts.analyzer import STDMAnalyzer

    try:
        analyzer = STDMAnalyzer(Path(data_dir))
        topic_data = analyzer.topic_analysis()

        if output_format == "table":
            table = Table(title="Topic Analysis")
            table.add_column("Topic", style="cyan")
            table.add_column("Turns", justify="right")
            table.add_column("Sessions", justify="right")
            table.add_column("Avg Turns/Session", justify="right")

            for row in topic_data.iter_rows(named=True):
                table.add_row(
                    str(row.get("ssot__TopicApiName__c", "Unknown")),
                    str(row.get("turn_count", 0)),
                    str(row.get("session_count", 0)),
                    f"{row.get('avg_turns_per_session', 0):.2f}",
                )

            console.print(table)
        elif output_format == "json":
            import json
            console.print(json.dumps(topic_data.to_dicts(), indent=2))
        elif output_format == "csv":
            console.print(topic_data.write_csv())

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--data-dir", type=click.Path(exists=True), required=True, help="Data directory")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "csv"]), default="table")
def actions(data_dir: str, output_format: str):
    """
    Show action distribution analysis.

    Lists the most frequently used actions (Flow/Apex invocations).

    Examples:

        stdm-extract actions --data-dir ./stdm_data
    """
    from scripts.analyzer import STDMAnalyzer

    try:
        analyzer = STDMAnalyzer(Path(data_dir))
        action_data = analyzer.action_distribution()

        if output_format == "table":
            table = Table(title="Action Distribution")
            table.add_column("Action Name", style="cyan")
            table.add_column("Count", justify="right")

            for row in action_data.iter_rows(named=True):
                table.add_row(
                    str(row.get("ssot__Name__c", "Unknown")),
                    str(row.get("count", 0)),
                )

            console.print(table)
        elif output_format == "json":
            import json
            console.print(json.dumps(action_data.to_dicts(), indent=2))
        elif output_format == "csv":
            console.print(action_data.write_csv())

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--org", required=True, help="Salesforce org alias")
@click.option("--consumer-key", help="Connected App consumer key")
@click.option("--entity", type=click.Choice(["sessions", "interactions", "steps", "messages"]),
              default="sessions", help="Entity to count")
@click.option("--days", default=7, help="Count last N days")
def count(org: str, consumer_key: Optional[str], entity: str, days: int):
    """
    Count records in Data Cloud.

    Quick way to check data volume before extraction.

    Examples:

        stdm-extract count --org prod --entity sessions --days 30
    """
    from scripts.datacloud_client import DataCloudClient
    from scripts.models import DMO_NAMES

    auth = get_auth(org, consumer_key)

    since = datetime.utcnow() - timedelta(days=days)
    timestamp_field = "ssot__StartTimestamp__c" if entity == "sessions" else None

    try:
        client = DataCloudClient(auth)
        dmo = DMO_NAMES[entity]

        where_clause = None
        if timestamp_field:
            where_clause = f"{timestamp_field} >= '{since.strftime('%Y-%m-%dT%H:%M:%S.000Z')}'"

        record_count = client.count(dmo, where_clause)

        console.print(f"\n[bold cyan]Record Count[/bold cyan]")
        console.print(f"Entity: {entity}")
        console.print(f"Period: Last {days} days")
        console.print(f"Count: [green]{record_count:,}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command("test-auth")
@click.option("--org", required=True, help="Salesforce org alias")
@click.option("--consumer-key", help="Connected App consumer key")
def test_auth(org: str, consumer_key: Optional[str]):
    """
    Test authentication to Data Cloud.

    Verifies JWT auth is configured correctly and can access Data Cloud.

    Examples:

        stdm-extract test-auth --org prod
    """
    auth = get_auth(org, consumer_key)

    console.print(f"\n[bold cyan]Testing Authentication[/bold cyan]")
    console.print(f"Org: {org}")

    try:
        # Get org info
        console.print(f"\n[dim]Getting org info...[/dim]")
        org_info = auth.org_info
        console.print(f"Instance: {org_info.instance_url}")
        console.print(f"Username: {org_info.username}")
        console.print(f"Sandbox: {org_info.is_sandbox}")

        # Test token generation
        console.print(f"\n[dim]Testing token generation...[/dim]")
        token = auth.get_token()
        console.print(f"[green]✓ Token generated[/green]")

        # Test Data Cloud connection
        console.print(f"\n[dim]Testing Data Cloud access...[/dim]")
        auth.test_connection()
        console.print(f"[green]✓ Data Cloud accessible[/green]")

        console.print(f"\n[bold green]Authentication successful![/bold green]")

    except Exception as e:
        console.print(f"\n[red]✗ Authentication failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
