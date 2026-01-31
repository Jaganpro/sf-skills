"""
T6 Live SQL Execution Test Fixtures

Provides fixtures for:
- Query execution with timeout handling
- Template variable substitution
- Error categorization and retry logic
- Result validation helpers
"""

import pytest
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path


# Query execution timeout (seconds)
QUERY_TIMEOUT = 120


@pytest.fixture(scope="session")
def query_patterns_content() -> str:
    """Load query-patterns.md content once per session."""
    skill_root = Path(__file__).parent.parent.parent.parent
    doc_path = skill_root / "resources" / "query-patterns.md"
    return doc_path.read_text()


@pytest.fixture(scope="session")
def all_sql_blocks(query_patterns_content: str) -> List[str]:
    """Extract all SQL blocks from query-patterns.md."""
    pattern = r'```sql\s*(.*?)```'
    matches = re.findall(pattern, query_patterns_content, re.DOTALL | re.IGNORECASE)
    return [m.strip() for m in matches if m.strip()]


@pytest.fixture(scope="session")
def sample_session_id(data_client) -> Optional[str]:
    """
    Get a real session ID from the org for template substitution.

    Returns None if no sessions exist (tests using this will be skipped).
    """
    try:
        sql = """
            SELECT ssot__Id__c
            FROM ssot__AIAgentSession__dlm
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 1
        """
        results = list(data_client.query(sql, limit=1))
        if results:
            return results[0].get("ssot__Id__c")
    except Exception:
        pass
    return None


@pytest.fixture(scope="session")
def sample_interaction_id(data_client) -> Optional[str]:
    """
    Get a real interaction ID from the org for template substitution.

    Returns None if no interactions exist.
    """
    try:
        sql = """
            SELECT ssot__Id__c
            FROM ssot__AIAgentInteraction__dlm
            ORDER BY ssot__StartTimestamp__c DESC
            LIMIT 1
        """
        results = list(data_client.query(sql, limit=1))
        if results:
            return results[0].get("ssot__Id__c")
    except Exception:
        pass
    return None


@pytest.fixture
def substitute_template_vars(sample_session_id, sample_interaction_id):
    """
    Factory fixture to substitute template variables in SQL queries.

    Replaces:
    - {{SESSION_ID}} with a real session ID
    - {{INTERACTION_ID}} with a real interaction ID
    - {{START_DATE}} with 30 days ago
    - {{END_DATE}} with now
    - {{USER_QUERY}} with a test search string
    - {{FILTER_CLAUSE}} with empty string
    - {{KNOWLEDGE_ARTICLE_DMO}} with placeholder

    Usage:
        def test_query(substitute_template_vars, data_client):
            sql = substitute_template_vars("SELECT * WHERE id = '{{SESSION_ID}}'")
            results = list(data_client.query(sql))
    """
    def _substitute(sql: str, skip_if_no_session: bool = True) -> str:
        # Session ID substitution
        if "{{SESSION_ID}}" in sql:
            if sample_session_id:
                sql = sql.replace("{{SESSION_ID}}", sample_session_id)
            elif skip_if_no_session:
                pytest.skip("No sessions available for template substitution")
            else:
                # Use a placeholder that will return no results
                sql = sql.replace("{{SESSION_ID}}", "00000000-0000-0000-0000-000000000000")

        # Interaction ID substitution
        if "{{INTERACTION_ID}}" in sql:
            if sample_interaction_id:
                sql = sql.replace("{{INTERACTION_ID}}", sample_interaction_id)
            elif skip_if_no_session:
                pytest.skip("No interactions available for template substitution")
            else:
                sql = sql.replace("{{INTERACTION_ID}}", "00000000-0000-0000-0000-000000000000")

        # Date substitutions
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        sql = sql.replace("{{START_DATE}}", start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        sql = sql.replace("{{END_DATE}}", end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"))

        # Knowledge retrieval placeholders
        sql = sql.replace("{{USER_QUERY}}", "test query")
        sql = sql.replace("{{FILTER_CLAUSE}}", "")
        sql = sql.replace("{{KNOWLEDGE_ARTICLE_DMO}}", "Knowledge_kav__dlm")

        # Agent names placeholder
        sql = sql.replace("{{AGENT_NAMES}}", "'Test_Agent'")
        sql = sql.replace("{{SESSION_IDS}}", f"'{sample_session_id or '00000000-0000-0000-0000-000000000000'}'")
        sql = sql.replace("{{INTERACTION_IDS}}", f"'{sample_interaction_id or '00000000-0000-0000-0000-000000000000'}'")

        return sql

    return _substitute


@pytest.fixture
def execute_query(data_client, substitute_template_vars):
    """
    Factory fixture to execute a query with template substitution and validation.

    Returns (success: bool, results: list, error: str or None)

    Usage:
        def test_query(execute_query):
            success, results, error = execute_query("SELECT * FROM ...")
            assert success, error
    """
    def _execute(
        sql: str,
        limit: int = 10,
        skip_if_template_missing: bool = True
    ) -> tuple:
        try:
            # Substitute template variables
            sql = substitute_template_vars(sql, skip_if_no_session=skip_if_template_missing)

            # Execute query
            results = list(data_client.query(sql, limit=limit))
            return (True, results, None)

        except pytest.skip.Exception:
            raise  # Re-raise skip exceptions
        except Exception as e:
            return (False, [], str(e))

    return _execute


def categorize_query_error(error_message: str) -> str:
    """
    Categorize a query error for better diagnostics.

    Returns one of:
    - "auth": Authentication/permission error
    - "syntax": SQL syntax error
    - "dmo_not_found": DMO doesn't exist
    - "field_not_found": Field doesn't exist
    - "timeout": Query timed out
    - "rate_limit": Rate limited
    - "unknown": Other error
    """
    error_lower = error_message.lower()

    if "unauthorized" in error_lower or "authentication" in error_lower:
        return "auth"
    if "syntax" in error_lower or "parse" in error_lower:
        return "syntax"
    if "object type" in error_lower and "not found" in error_lower:
        return "dmo_not_found"
    if "field" in error_lower and "not found" in error_lower:
        return "field_not_found"
    if "timeout" in error_lower:
        return "timeout"
    if "rate limit" in error_lower or "429" in error_lower:
        return "rate_limit"

    return "unknown"


class QueryResult:
    """Helper class for query result validation."""

    def __init__(self, success: bool, results: List[Dict[str, Any]], error: Optional[str] = None):
        self.success = success
        self.results = results
        self.error = error
        self.error_category = categorize_query_error(error) if error else None

    @property
    def row_count(self) -> int:
        return len(self.results)

    @property
    def columns(self) -> List[str]:
        if self.results:
            return list(self.results[0].keys())
        return []

    def has_column(self, column_name: str) -> bool:
        return column_name in self.columns

    def has_any_column(self, column_names: List[str]) -> bool:
        return any(col in self.columns for col in column_names)
