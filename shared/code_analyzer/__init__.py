"""
Salesforce Code Analyzer V5 Integration for sf-skills.

This module provides shared infrastructure for integrating Salesforce Code Analyzer
with Claude Code's hook system across all sf-skills (apex, flow, lwc, etc.).

Components:
    - scanner: Core wrapper for sf code-analyzer CLI
    - parser: JSON result normalization
    - dependency_checker: Runtime dependency detection (JDK, Node, Python)
    - score_merger: Combines custom scoring with CA findings
    - formatter: Terminal output formatting

Usage:
    from code_analyzer import CodeAnalyzerScanner, SkillType, ScoreMerger

    scanner = CodeAnalyzerScanner()
    result = scanner.scan("/path/to/file.cls", SkillType.APEX)

    merger = ScoreMerger(custom_scores, max_scores)
    merged = merger.merge(result.violations)
"""

from .scanner import CodeAnalyzerScanner, SkillType, ScanResult
from .dependency_checker import DependencyChecker
from .score_merger import ScoreMerger, MergedScore
from .parser import parse_ca_output, normalize_violation
from .formatter import format_validation_output

__all__ = [
    # Scanner
    "CodeAnalyzerScanner",
    "SkillType",
    "ScanResult",
    # Dependencies
    "DependencyChecker",
    # Scoring
    "ScoreMerger",
    "MergedScore",
    # Parser
    "parse_ca_output",
    "normalize_violation",
    # Formatter
    "format_validation_output",
]

__version__ = "1.0.0"
