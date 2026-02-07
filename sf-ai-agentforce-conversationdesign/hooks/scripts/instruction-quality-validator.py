#!/usr/bin/env python3
"""
Instruction Quality Validator for Agentforce Conversation Design

Validates instruction writing quality in conversation design files.
Detects anti-patterns like negative framing, over-constraining language,
business rules in instructions, and semantic overlap between topics.

All checks are ADVISORY - they provide warnings but do not block operations.
"""

import json
import re
import select
import sys
from collections import Counter
from typing import Dict, List, Tuple, Set


def read_stdin_safe(timeout_seconds: float = 0.1) -> dict:
    """
    Safely read JSON from stdin with timeout.

    Returns empty dict if:
    - stdin is a TTY (interactive terminal)
    - No data available within timeout
    - JSON parsing fails

    Args:
        timeout_seconds: How long to wait for stdin data (default 0.1s)

    Returns:
        Parsed JSON dict, or empty dict on any error
    """
    # Skip if running interactively
    if sys.stdin.isatty():
        return {}

    try:
        # Use select to check if stdin has data (Unix only)
        readable, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
        if not readable:
            return {}

        # Read and parse
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, OSError, ValueError):
        return {}


class InstructionQualityValidator:
    """Validates conversation design instruction quality."""

    # Negative framing patterns
    NEGATIVE_PATTERNS = [
        r"\bdon't\b", r"\bdo not\b", r"\bnever\b",
        r"\bmust not\b", r"\bshould not\b", r"\bcannot\b", r"\bcan't\b"
    ]

    # Constraining words
    CONSTRAINING_WORDS = [
        r"\bmust\b", r"\balways\b", r"\bnever\b",
        r"\brequired\b", r"\bmandatory\b"
    ]

    # Business rule patterns
    BUSINESS_RULE_PATTERNS = [
        r"\bif\b.*\bthen\b",
        r"\bwhen\b.*\b(check|verify|ensure|validate)\b",
        r"\bcalculate\b",
        r"\bvalidate\b.*\bformat\b",
        r"\b[a-z]+@[a-z]+\.[a-z]+\b",  # email pattern
        r"\b\(\d{3}\)\s?\d{3}-\d{4}\b",  # phone pattern
        r"\b\d{2}/\d{2}/\d{4}\b",  # date pattern
    ]

    # Format validation patterns
    FORMAT_VALIDATION_PATTERNS = [
        r"verify\s+(email|phone|date)\s+format",
        r"check\s+(email|phone)\s+number",
        r"validate\s+(email|phone|SSN|credit\s+card)",
        r"regex|regular\s+expression",
        r"pattern\s+match",
    ]

    def __init__(self, file_path: str, content: str):
        """
        Initialize the instruction quality validator.

        Args:
            file_path: Path to the file being validated
            content: Content of the file
        """
        self.file_path = file_path
        self.content = content
        self.lines = content.split('\n')
        self.warnings = []
        self.errors = []
        self.info_messages = []

    def is_in_scope(self) -> bool:
        """
        Check if this file should be validated.

        Returns:
            True if file is a .md file in the conversationdesign skill
        """
        return (
            self.file_path.endswith('.md') and
            'sf-ai-agentforce-conversationdesign' in self.file_path
        )

    def validate(self) -> None:
        """Run all validation checks."""
        if not self.is_in_scope():
            return

        self._check_negative_framing()
        self._check_over_constraining()
        self._check_business_rules()
        self._check_format_validation()
        self._check_instruction_length()
        self._check_semantic_overlap()

    def _is_instruction_context(self, line_num: int, line: str) -> bool:
        """
        Check if a line is in an instruction-like context.

        Args:
            line_num: Line number (0-indexed)
            line: The line content

        Returns:
            True if line is in instruction context
        """
        # Look at surrounding lines for instruction markers
        context_start = max(0, line_num - 3)
        context_end = min(len(self.lines), line_num + 3)
        context = '\n'.join(self.lines[context_start:context_end]).lower()

        # Check for instruction-related keywords
        instruction_markers = [
            'instruction', 'guideline', 'should', 'must',
            'template', 'example', 'topic', 'classification'
        ]

        return any(marker in context for marker in instruction_markers)

    def _check_negative_framing(self) -> None:
        """Check for negative framing in instructions."""
        for line_num, line in enumerate(self.lines):
            # Only check instruction-like contexts
            if not self._is_instruction_context(line_num, line):
                continue

            for pattern in self.NEGATIVE_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    snippet = line.strip()[:80]
                    if len(line.strip()) > 80:
                        snippet += "..."

                    self.warnings.append(
                        f"⚠️ NEGATIVE FRAMING (line {line_num + 1}): \"{snippet}\" — "
                        f"Consider positive reframing: \"Always...\" instead of \"Don't...\""
                    )
                    break  # Only report once per line

    def _check_over_constraining(self) -> None:
        """Check for over-constraining language in sections."""
        # Split content into sections (between markdown headers)
        sections = self._split_into_sections()

        for section_title, section_content in sections:
            if not section_content.strip():
                continue

            # Count constraining words
            word_count = len(section_content.split())
            if word_count < 10:  # Skip very short sections
                continue

            constraining_count = 0
            for pattern in self.CONSTRAINING_WORDS:
                constraining_count += len(re.findall(pattern, section_content, re.IGNORECASE))

            # Calculate density per 100 words
            density = (constraining_count / word_count) * 100

            if density > 3:  # Threshold: >3 per 100 words
                self.warnings.append(
                    f"⚠️ OVER-CONSTRAINING: Section \"{section_title[:40]}\" has "
                    f"{density:.1f} constraining terms per 100 words (threshold: 3) — "
                    f"Consider using \"should\" or \"recommended\""
                )

    def _split_into_sections(self) -> List[Tuple[str, str]]:
        """
        Split content into sections based on markdown headers.

        Returns:
            List of (section_title, section_content) tuples
        """
        sections = []
        current_title = "Introduction"
        current_content = []

        for line in self.lines:
            # Check if line is a markdown header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_content:
                    sections.append((current_title, '\n'.join(current_content)))

                # Start new section
                current_title = header_match.group(2)
                current_content = []
            else:
                current_content.append(line)

        # Save final section
        if current_content:
            sections.append((current_title, '\n'.join(current_content)))

        return sections

    def _check_business_rules(self) -> None:
        """Check for business rules/logic in instructions."""
        for line_num, line in enumerate(self.lines):
            # Only check instruction-like contexts
            if not self._is_instruction_context(line_num, line):
                continue

            for pattern in self.BUSINESS_RULE_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    snippet = line.strip()[:80]
                    if len(line.strip()) > 80:
                        snippet += "..."

                    self.errors.append(
                        f"❌ BUSINESS RULE IN INSTRUCTIONS (line {line_num + 1}): \"{snippet}\" — "
                        f"Move this logic to a Flow or Apex action"
                    )
                    break  # Only report once per line

    def _check_format_validation(self) -> None:
        """Check for format validation logic in instructions."""
        for line_num, line in enumerate(self.lines):
            # Only check instruction-like contexts
            if not self._is_instruction_context(line_num, line):
                continue

            for pattern in self.FORMAT_VALIDATION_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    snippet = line.strip()[:80]
                    if len(line.strip()) > 80:
                        snippet += "..."

                    self.errors.append(
                        f"❌ FORMAT VALIDATION IN INSTRUCTIONS (line {line_num + 1}): \"{snippet}\" — "
                        f"Use Flow/Apex validation instead"
                    )
                    break  # Only report once per line

    def _check_instruction_length(self) -> None:
        """Check for overly long instruction sections."""
        sections = self._split_into_sections()

        for section_title, section_content in sections:
            # Count words (excluding code blocks and headers)
            content_lines = [
                line for line in section_content.split('\n')
                if not line.strip().startswith('#') and
                   not line.strip().startswith('```')
            ]
            word_count = sum(len(line.split()) for line in content_lines)

            if word_count > 500:
                self.info_messages.append(
                    f"ℹ️ LONG INSTRUCTION SECTION: \"{section_title[:40]}\" has "
                    f"{word_count} words (recommended: <500) — "
                    f"Consider splitting into sub-topics"
                )

    def _extract_significant_words(self, text: str) -> Set[str]:
        """
        Extract significant words from text (excluding stop words).

        Args:
            text: Text to analyze

        Returns:
            Set of significant words in lowercase
        """
        # Common stop words to exclude
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for',
            'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on',
            'that', 'the', 'to', 'was', 'will', 'with', 'this', 'they',
            'their', 'them', 'these', 'those', 'what', 'when', 'where',
            'which', 'who', 'why', 'how', 'can', 'should', 'would', 'could'
        }

        # Extract words (alphanumeric only)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())

        # Filter out stop words
        return {word for word in words if word not in stop_words}

    def _check_semantic_overlap(self) -> None:
        """Check for semantic overlap between topic classifications."""
        # Extract topic classification descriptions
        topics = self._extract_topic_descriptions()

        if len(topics) < 2:
            return  # Need at least 2 topics to compare

        # Compare each pair of topics
        for i, (topic1_name, topic1_desc) in enumerate(topics):
            for topic2_name, topic2_desc in topics[i + 1:]:
                overlap_pct = self._calculate_semantic_overlap(topic1_desc, topic2_desc)

                if overlap_pct > 0.5:  # >50% overlap
                    self.warnings.append(
                        f"⚠️ SEMANTIC OVERLAP: Topics \"{topic1_name}\" and \"{topic2_name}\" "
                        f"share {int(overlap_pct * 100)}% vocabulary — "
                        f"Ensure classification descriptions are distinct"
                    )

    def _extract_topic_descriptions(self) -> List[Tuple[str, str]]:
        """
        Extract topic names and their classification descriptions.

        Returns:
            List of (topic_name, description) tuples
        """
        topics = []
        current_topic = None
        in_description = False
        description_lines = []

        for line in self.lines:
            # Look for topic headers
            topic_match = re.match(r'^#{2,4}\s+(?:Topic\s+\d+:\s+)?(.+)$', line, re.IGNORECASE)
            if topic_match:
                # Save previous topic if exists
                if current_topic and description_lines:
                    topics.append((current_topic, '\n'.join(description_lines)))

                current_topic = topic_match.group(1).strip()
                in_description = False
                description_lines = []

            # Look for classification/description markers
            elif re.search(r'classification|description|when to use|purpose', line, re.IGNORECASE):
                in_description = True
            elif in_description and line.strip() and not line.strip().startswith('#'):
                description_lines.append(line)

        # Save final topic
        if current_topic and description_lines:
            topics.append((current_topic, '\n'.join(description_lines)))

        return topics

    def _calculate_semantic_overlap(self, text1: str, text2: str) -> float:
        """
        Calculate semantic overlap between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Overlap percentage (0.0 to 1.0)
        """
        words1 = self._extract_significant_words(text1)
        words2 = self._extract_significant_words(text2)

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def generate_output(self) -> str:
        """
        Generate output for Claude Code.

        Returns:
            Formatted output string (empty if no issues)
        """
        if not (self.warnings or self.errors or self.info_messages):
            return ""

        output_lines = []

        # Output all diagnostics
        for error in self.errors:
            output_lines.append(error)

        for warning in self.warnings:
            output_lines.append(warning)

        for info in self.info_messages:
            output_lines.append(info)

        # Summary line
        warning_count = len(self.warnings)
        error_count = len(self.errors)
        output_lines.append(
            f"📊 Instruction Quality: {warning_count} warnings, {error_count} errors found"
        )

        return '\n'.join(output_lines)


def main():
    """Main entry point for the hook script."""
    # Read JSON from stdin
    input_data = read_stdin_safe()

    if not input_data:
        # No data from stdin, exit silently
        sys.exit(0)

    # Extract file path and content
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Handle both Write and Edit tools
    file_path = tool_input.get('file_path', '')

    if tool_name == 'Write':
        content = tool_input.get('content', '')
    elif tool_name == 'Edit':
        # For Edit, we only check the new_string
        content = tool_input.get('new_string', '')
    else:
        # Not a Write/Edit tool, exit silently
        sys.exit(0)

    # Validate
    validator = InstructionQualityValidator(file_path, content)
    validator.validate()

    # Output results
    output = validator.generate_output()
    if output:
        print(output)

    # Always exit 0 (never block operations)
    sys.exit(0)


if __name__ == "__main__":
    main()
