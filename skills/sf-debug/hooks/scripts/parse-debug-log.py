#!/usr/bin/env python3
"""
Parse Salesforce debug logs and provide analysis for Claude auto-fix loop.

This hook parses debug log output from `sf apex get log` or `sf apex tail log`
and provides structured analysis including:
- Governor limit usage
- Performance hotspots
- Exceptions and stack traces
- Optimization recommendations

Environment Variables:
    TOOL_OUTPUT: The stdout from the Bash command
    TOOL_INPUT: The command that was executed
"""

import json
import os
import sys
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Only process debug log commands
def should_process() -> bool:
    """Check if this is a debug log command we should process."""
    tool_input = os.environ.get('TOOL_INPUT', '')
    log_commands = ['sf apex get log', 'sf apex tail log', 'sf apex list log']
    return any(cmd in tool_input for cmd in log_commands)

@dataclass
class LimitUsage:
    """Tracks governor limit usage."""
    soql_queries: int = 0
    soql_limit: int = 100
    dml_statements: int = 0
    dml_limit: int = 150
    dml_rows: int = 0
    dml_rows_limit: int = 10000
    cpu_time: int = 0
    cpu_limit: int = 10000
    heap_size: int = 0
    heap_limit: int = 6000000
    callouts: int = 0
    callout_limit: int = 100

@dataclass
class QueryInfo:
    """Information about a SOQL query."""
    line_number: int
    query: str
    rows_returned: int
    execution_time_ms: float
    is_in_loop: bool = False

@dataclass
class DMLInfo:
    """Information about a DML operation."""
    line_number: int
    operation: str  # INSERT, UPDATE, DELETE, UPSERT
    rows_affected: int
    is_in_loop: bool = False

@dataclass
class ExceptionInfo:
    """Information about an exception."""
    exception_type: str
    message: str
    line_number: int
    stack_trace: List[str] = field(default_factory=list)

@dataclass
class LogAnalysis:
    """Complete analysis of a debug log."""
    limits: LimitUsage = field(default_factory=LimitUsage)
    queries: List[QueryInfo] = field(default_factory=list)
    dml_operations: List[DMLInfo] = field(default_factory=list)
    exceptions: List[ExceptionInfo] = field(default_factory=list)
    execution_time_ms: float = 0
    entry_point: str = ""
    warnings: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)

def parse_debug_log(log_content: str) -> LogAnalysis:
    """
    Parse a Salesforce debug log and extract key metrics.

    Args:
        log_content: Raw debug log text

    Returns:
        LogAnalysis with parsed information
    """
    analysis = LogAnalysis()

    lines = log_content.split('\n')
    in_loop_depth = 0
    current_method = ""
    query_start_times: Dict[int, float] = {}

    for i, line in enumerate(lines):
        # Track loop depth
        if '|LOOP_BEGIN|' in line or '|ITERATION_BEGIN|' in line:
            in_loop_depth += 1
        elif '|LOOP_END|' in line or '|ITERATION_END|' in line:
            in_loop_depth = max(0, in_loop_depth - 1)

        # Track method context
        if '|METHOD_ENTRY|' in line or '|CODE_UNIT_STARTED|' in line:
            match = re.search(r'\|(?:METHOD_ENTRY|CODE_UNIT_STARTED)\|.*?\|(.*?)(?:\||$)', line)
            if match:
                current_method = match.group(1)
                if not analysis.entry_point:
                    analysis.entry_point = current_method

        # Parse SOQL queries
        if '|SOQL_EXECUTE_BEGIN|' in line:
            match = re.search(r'\[(\d+)\].*?SELECT', line, re.IGNORECASE)
            if match:
                line_num = int(match.group(1))
                query_match = re.search(r'SELECT.*', line, re.IGNORECASE)
                query_text = query_match.group(0) if query_match else "Unknown query"

                query_info = QueryInfo(
                    line_number=line_num,
                    query=query_text[:200],  # Truncate long queries
                    rows_returned=0,
                    execution_time_ms=0,
                    is_in_loop=in_loop_depth > 0
                )
                analysis.queries.append(query_info)
                analysis.limits.soql_queries += 1

        # Parse SOQL results
        if '|SOQL_EXECUTE_END|' in line and analysis.queries:
            match = re.search(r'\[(\d+)\s*rows?\]', line)
            if match and analysis.queries:
                analysis.queries[-1].rows_returned = int(match.group(1))

        # Parse DML operations
        if '|DML_BEGIN|' in line:
            match = re.search(r'\[(\d+)\].*?\|(INSERT|UPDATE|DELETE|UPSERT)', line, re.IGNORECASE)
            if match:
                dml_info = DMLInfo(
                    line_number=int(match.group(1)),
                    operation=match.group(2).upper(),
                    rows_affected=0,
                    is_in_loop=in_loop_depth > 0
                )
                analysis.dml_operations.append(dml_info)
                analysis.limits.dml_statements += 1

        # Parse DML rows
        if '|DML_END|' in line and analysis.dml_operations:
            match = re.search(r'\[(\d+)\s*rows?\]', line)
            if match and analysis.dml_operations:
                rows = int(match.group(1))
                analysis.dml_operations[-1].rows_affected = rows
                analysis.limits.dml_rows += rows

        # Parse exceptions
        if '|EXCEPTION_THROWN|' in line:
            match = re.search(r'\[(\d+)\]\|([^|]+)\|(.+)', line)
            if match:
                exception = ExceptionInfo(
                    exception_type=match.group(2),
                    message=match.group(3),
                    line_number=int(match.group(1))
                )
                analysis.exceptions.append(exception)

        # Parse fatal errors
        if '|FATAL_ERROR|' in line:
            match = re.search(r'\|FATAL_ERROR\|(.+)', line)
            if match and not analysis.exceptions:
                analysis.exceptions.append(ExceptionInfo(
                    exception_type="FATAL_ERROR",
                    message=match.group(1),
                    line_number=0
                ))

        # Parse limit usage
        if '|LIMIT_USAGE' in line:
            # Parse limit usage lines
            limit_patterns = {
                'SOQL_QUERIES': ('soql_queries', 'soql_limit'),
                'DML_STATEMENTS': ('dml_statements', 'dml_limit'),
                'DML_ROWS': ('dml_rows', 'dml_rows_limit'),
                'CPU_TIME': ('cpu_time', 'cpu_limit'),
                'HEAP_SIZE': ('heap_size', 'heap_limit'),
                'CALLOUTS': ('callouts', 'callout_limit'),
            }

            for limit_name, (used_attr, limit_attr) in limit_patterns.items():
                if limit_name in line:
                    match = re.search(rf'{limit_name}\|(\d+)\|(\d+)', line)
                    if match:
                        setattr(analysis.limits, used_attr, int(match.group(1)))
                        setattr(analysis.limits, limit_attr, int(match.group(2)))

        # Parse execution time
        if '|EXECUTION_FINISHED|' in line:
            match = re.search(r'(\d+(?:\.\d+)?)\s*ms', line)
            if match:
                analysis.execution_time_ms = float(match.group(1))

    # Analyze for issues
    analyze_issues(analysis)

    return analysis

def analyze_issues(analysis: LogAnalysis) -> None:
    """Analyze the parsed log for issues and add warnings/critical issues."""

    limits = analysis.limits

    # Check for SOQL in loops
    loop_queries = [q for q in analysis.queries if q.is_in_loop]
    if loop_queries:
        analysis.critical_issues.append(
            f"SOQL in loop detected: {len(loop_queries)} queries executed inside loops"
        )

    # Check for DML in loops
    loop_dml = [d for d in analysis.dml_operations if d.is_in_loop]
    if loop_dml:
        analysis.critical_issues.append(
            f"DML in loop detected: {len(loop_dml)} DML operations inside loops"
        )

    # Check SOQL limit
    soql_percent = (limits.soql_queries / limits.soql_limit) * 100 if limits.soql_limit else 0
    if soql_percent >= 95:
        analysis.critical_issues.append(
            f"SOQL limit critical: {limits.soql_queries}/{limits.soql_limit} ({soql_percent:.1f}%)"
        )
    elif soql_percent >= 80:
        analysis.warnings.append(
            f"SOQL limit warning: {limits.soql_queries}/{limits.soql_limit} ({soql_percent:.1f}%)"
        )

    # Check DML limit
    dml_percent = (limits.dml_statements / limits.dml_limit) * 100 if limits.dml_limit else 0
    if dml_percent >= 95:
        analysis.critical_issues.append(
            f"DML limit critical: {limits.dml_statements}/{limits.dml_limit} ({dml_percent:.1f}%)"
        )
    elif dml_percent >= 80:
        analysis.warnings.append(
            f"DML limit warning: {limits.dml_statements}/{limits.dml_limit} ({dml_percent:.1f}%)"
        )

    # Check CPU limit
    cpu_percent = (limits.cpu_time / limits.cpu_limit) * 100 if limits.cpu_limit else 0
    if cpu_percent >= 95:
        analysis.critical_issues.append(
            f"CPU limit critical: {limits.cpu_time}/{limits.cpu_limit}ms ({cpu_percent:.1f}%)"
        )
    elif cpu_percent >= 80:
        analysis.warnings.append(
            f"CPU limit warning: {limits.cpu_time}/{limits.cpu_limit}ms ({cpu_percent:.1f}%)"
        )

    # Check heap limit
    heap_percent = (limits.heap_size / limits.heap_limit) * 100 if limits.heap_limit else 0
    if heap_percent >= 95:
        analysis.critical_issues.append(
            f"Heap limit critical: {limits.heap_size}/{limits.heap_limit} bytes ({heap_percent:.1f}%)"
        )
    elif heap_percent >= 80:
        analysis.warnings.append(
            f"Heap limit warning: {limits.heap_size}/{limits.heap_limit} bytes ({heap_percent:.1f}%)"
        )

    # Check for large queries
    large_queries = [q for q in analysis.queries if q.rows_returned > 10000]
    if large_queries:
        analysis.warnings.append(
            f"Large queries detected: {len(large_queries)} queries returned >10,000 rows"
        )

    # Check for exceptions
    if analysis.exceptions:
        for exc in analysis.exceptions:
            analysis.critical_issues.append(
                f"Exception: {exc.exception_type} at line {exc.line_number}"
            )

def format_output(analysis: LogAnalysis) -> str:
    """Format the analysis for Claude consumption."""
    lines = []

    lines.append("=" * 60)
    lines.append("🔍 DEBUG LOG ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    # Entry point
    if analysis.entry_point:
        lines.append(f"📍 Entry Point: {analysis.entry_point}")
        lines.append("")

    # Critical Issues
    if analysis.critical_issues:
        lines.append("🔴 CRITICAL ISSUES")
        lines.append("-" * 60)
        for issue in analysis.critical_issues:
            lines.append(f"   • {issue}")
        lines.append("")

    # Warnings
    if analysis.warnings:
        lines.append("🟠 WARNINGS")
        lines.append("-" * 60)
        for warning in analysis.warnings:
            lines.append(f"   • {warning}")
        lines.append("")

    # Governor Limits
    limits = analysis.limits
    lines.append("📊 GOVERNOR LIMIT USAGE")
    lines.append("-" * 60)

    def limit_bar(used: int, limit: int, name: str) -> str:
        pct = (used / limit * 100) if limit else 0
        icon = "🔴" if pct >= 95 else "🟠" if pct >= 80 else "✅"
        return f"   {icon} {name}: {used}/{limit} ({pct:.1f}%)"

    lines.append(limit_bar(limits.soql_queries, limits.soql_limit, "SOQL Queries"))
    lines.append(limit_bar(limits.dml_statements, limits.dml_limit, "DML Statements"))
    lines.append(limit_bar(limits.dml_rows, limits.dml_rows_limit, "DML Rows"))
    lines.append(limit_bar(limits.cpu_time, limits.cpu_limit, "CPU Time (ms)"))
    lines.append(limit_bar(limits.heap_size, limits.heap_limit, "Heap Size"))
    lines.append(limit_bar(limits.callouts, limits.callout_limit, "Callouts"))
    lines.append("")

    # Queries in loops
    loop_queries = [q for q in analysis.queries if q.is_in_loop]
    if loop_queries:
        lines.append("🔴 SOQL QUERIES IN LOOPS (Must Fix)")
        lines.append("-" * 60)
        for q in loop_queries[:5]:  # Show first 5
            lines.append(f"   Line {q.line_number}: {q.query[:80]}...")
            lines.append(f"      Rows: {q.rows_returned}")
        if len(loop_queries) > 5:
            lines.append(f"   ... and {len(loop_queries) - 5} more")
        lines.append("")

    # DML in loops
    loop_dml = [d for d in analysis.dml_operations if d.is_in_loop]
    if loop_dml:
        lines.append("🔴 DML OPERATIONS IN LOOPS (Must Fix)")
        lines.append("-" * 60)
        for d in loop_dml[:5]:
            lines.append(f"   Line {d.line_number}: {d.operation} ({d.rows_affected} rows)")
        if len(loop_dml) > 5:
            lines.append(f"   ... and {len(loop_dml) - 5} more")
        lines.append("")

    # Exceptions
    if analysis.exceptions:
        lines.append("❌ EXCEPTIONS")
        lines.append("-" * 60)
        for exc in analysis.exceptions:
            lines.append(f"   {exc.exception_type}")
            lines.append(f"      Line: {exc.line_number}")
            lines.append(f"      Message: {exc.message[:100]}...")
        lines.append("")

    # Fix suggestions
    if analysis.critical_issues or analysis.warnings:
        lines.append("=" * 60)
        lines.append("🤖 AGENTIC FIX RECOMMENDATIONS")
        lines.append("=" * 60)
        lines.append("")

        if loop_queries:
            lines.append("For SOQL in loop:")
            lines.append("   1. Move query BEFORE the loop")
            lines.append("   2. Store results in Map<Id, SObject>")
            lines.append("   3. Access from Map inside loop")
            lines.append("")

        if loop_dml:
            lines.append("For DML in loop:")
            lines.append("   1. Create List<SObject> before loop")
            lines.append("   2. Add records to list inside loop")
            lines.append("   3. Single DML statement after loop")
            lines.append("")

        if analysis.exceptions:
            lines.append("For exceptions:")
            lines.append("   1. Read the source file at the line number")
            lines.append("   2. Add null checks or try-catch as appropriate")
            lines.append("   3. Use sf-apex skill to generate fix")
            lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)

def main():
    """Main entry point."""
    if not should_process():
        sys.exit(0)

    output = os.environ.get('TOOL_OUTPUT', '')

    if not output:
        sys.exit(0)

    # Check if this looks like a debug log
    log_indicators = [
        'EXECUTION_STARTED',
        'CODE_UNIT_STARTED',
        'SOQL_EXECUTE',
        'DML_BEGIN',
        'LIMIT_USAGE',
        'METHOD_ENTRY'
    ]

    if not any(indicator in output for indicator in log_indicators):
        sys.exit(0)

    try:
        analysis = parse_debug_log(output)

        # Only output if there's something interesting to report
        if (analysis.critical_issues or analysis.warnings or
            analysis.exceptions or analysis.limits.soql_queries > 0):
            formatted = format_output(analysis)
            print(formatted)
    except Exception as e:
        # Silently fail - don't block on parsing errors
        sys.exit(0)

if __name__ == "__main__":
    main()
