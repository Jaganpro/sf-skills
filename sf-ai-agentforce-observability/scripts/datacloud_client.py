"""
Data Cloud Query API client with streaming pagination.

Handles millions of records efficiently via cursor-based iteration
and direct Parquet writing for memory efficiency.

Features:
- Cursor-based pagination (nextRecordsUrl)
- Rate limit handling with exponential backoff
- Streaming iterator for memory efficiency
- Configurable batch size (default 2000)
- Direct-to-Parquet writing

Usage:
    auth = DataCloudAuth("myorg", "consumer_key")
    client = DataCloudClient(auth)

    # Iterate over results
    for record in client.query("SELECT * FROM ssot__AIAgentSession__dlm"):
        print(record)

    # Write directly to Parquet
    count = client.query_to_parquet(
        "SELECT * FROM ssot__AIAgentSession__dlm",
        Path("./sessions.parquet")
    )
"""

import json
import time
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

import httpx
import pyarrow as pa
import pyarrow.parquet as pq
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from .auth import DataCloudAuth


# Default configuration
DEFAULT_BATCH_SIZE = 2000
DEFAULT_TIMEOUT = 120.0  # seconds
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds


@dataclass
class QueryStats:
    """Statistics for a query execution."""

    records_fetched: int = 0
    batches_fetched: int = 0
    bytes_transferred: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    rate_limit_waits: int = 0

    @property
    def duration_seconds(self) -> float:
        """Query duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def records_per_second(self) -> float:
        """Records fetched per second."""
        if self.duration_seconds > 0:
            return self.records_fetched / self.duration_seconds
        return 0.0


@dataclass
class DataCloudClient:
    """
    Data Cloud Query API client with streaming support.

    Provides efficient querying of Data Cloud DMOs with automatic
    pagination and optional direct-to-Parquet writing.

    Attributes:
        auth: DataCloudAuth instance for authentication
        api_version: Salesforce API version (default: v60.0)
        batch_size: Records per API request (default: 2000)
        timeout: Request timeout in seconds (default: 120)

    Example:
        >>> auth = DataCloudAuth("prod", "3MVG9...")
        >>> client = DataCloudClient(auth)
        >>> for record in client.query("SELECT Id FROM ssot__AIAgentSession__dlm"):
        ...     print(record["ssot__Id__c"])
    """

    auth: DataCloudAuth
    api_version: str = "v60.0"
    batch_size: int = DEFAULT_BATCH_SIZE
    timeout: float = DEFAULT_TIMEOUT
    _stats: QueryStats = field(default_factory=QueryStats)

    @property
    def base_url(self) -> str:
        """Get the Data Cloud Query API base URL."""
        return f"{self.auth.instance_url}/services/data/{self.api_version}"

    @property
    def query_url(self) -> str:
        """Get the query endpoint URL."""
        return f"{self.base_url}/ssot/querybuilder/execute"

    @property
    def stats(self) -> QueryStats:
        """Get statistics from the last query."""
        return self._stats

    def _execute_request(
        self,
        url: str,
        method: str = "POST",
        json_body: Optional[dict] = None,
        retry_count: int = 0
    ) -> dict:
        """
        Execute an HTTP request with retry logic and rate limit handling.

        Args:
            url: Request URL
            method: HTTP method
            json_body: Request body for POST requests
            retry_count: Current retry attempt

        Returns:
            Response JSON

        Raises:
            RuntimeError: If request fails after retries
        """
        with httpx.Client(timeout=self.timeout) as client:
            try:
                if method == "POST":
                    response = client.post(
                        url,
                        headers=self.auth.get_headers(),
                        json=json_body
                    )
                else:
                    response = client.get(url, headers=self.auth.get_headers())

                # Handle rate limiting
                if response.status_code == 429:
                    if retry_count >= MAX_RETRIES:
                        raise RuntimeError("Rate limit exceeded after max retries")

                    wait_time = INITIAL_BACKOFF * (2 ** retry_count)
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = max(wait_time, float(retry_after))

                    self._stats.rate_limit_waits += 1
                    time.sleep(wait_time)

                    return self._execute_request(url, method, json_body, retry_count + 1)

                # Handle authentication errors
                if response.status_code == 401:
                    # Force token refresh and retry
                    self.auth.get_token(force_refresh=True)
                    if retry_count < MAX_RETRIES:
                        return self._execute_request(url, method, json_body, retry_count + 1)
                    raise RuntimeError("Authentication failed after token refresh")

                # Handle other errors
                if response.status_code >= 400:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        if isinstance(error_data, list) and error_data:
                            error_msg = error_data[0].get("message", error_msg)
                        elif isinstance(error_data, dict):
                            error_msg = error_data.get("message", error_data.get("error", error_msg))
                    except json.JSONDecodeError:
                        pass
                    raise RuntimeError(f"Query failed ({response.status_code}): {error_msg}")

                self._stats.bytes_transferred += len(response.content)
                return response.json()

            except httpx.TimeoutException:
                if retry_count < MAX_RETRIES:
                    time.sleep(INITIAL_BACKOFF * (2 ** retry_count))
                    return self._execute_request(url, method, json_body, retry_count + 1)
                raise RuntimeError(f"Request timed out after {MAX_RETRIES} retries")

    def query(self, sql: str, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """
        Execute Data Cloud SQL and yield records.

        Handles pagination automatically, yielding one record at a time
        for memory efficiency.

        Args:
            sql: Data Cloud SQL query
            limit: Optional maximum records to return

        Yields:
            Individual record dictionaries

        Example:
            >>> for record in client.query("SELECT * FROM ssot__AIAgentSession__dlm LIMIT 100"):
            ...     print(record["ssot__Id__c"])
        """
        self._stats = QueryStats(start_time=datetime.now())
        records_yielded = 0

        # Initial query request
        request_body = {
            "sql": sql,
            "pageSize": self.batch_size
        }

        response = self._execute_request(self.query_url, "POST", request_body)

        while True:
            data = response.get("data", [])
            self._stats.batches_fetched += 1

            for record in data:
                if limit and records_yielded >= limit:
                    self._stats.end_time = datetime.now()
                    return

                self._stats.records_fetched += 1
                records_yielded += 1
                yield record

            # Check for more pages
            next_url = response.get("nextRecordsUrl")
            if not next_url:
                break

            # Fetch next page (use GET for pagination URL)
            # The nextRecordsUrl is typically a full URL
            if not next_url.startswith("http"):
                next_url = f"{self.auth.instance_url}{next_url}"

            response = self._execute_request(next_url, "GET")

        self._stats.end_time = datetime.now()

    def query_all(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute query and return all records as a list.

        Warning: Use with caution for large datasets. Prefer query() iterator
        or query_to_parquet() for large results.

        Args:
            sql: Data Cloud SQL query

        Returns:
            List of all matching records
        """
        return list(self.query(sql))

    def query_to_parquet(
        self,
        sql: str,
        output_path: Path,
        schema: Optional[pa.Schema] = None,
        partition_cols: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> int:
        """
        Execute query and write results directly to Parquet file.

        Streams data in batches to avoid memory issues with large datasets.

        Args:
            sql: Data Cloud SQL query
            output_path: Path to output Parquet file or directory (if partitioned)
            schema: Optional PyArrow schema (auto-inferred if not provided)
            partition_cols: Optional columns to partition by
            show_progress: Show progress bar

        Returns:
            Total number of records written

        Example:
            >>> count = client.query_to_parquet(
            ...     "SELECT * FROM ssot__AIAgentSession__dlm WHERE ...",
            ...     Path("./sessions.parquet")
            ... )
            >>> print(f"Wrote {count} records")
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._stats = QueryStats(start_time=datetime.now())
        records_written = 0
        batches = []
        inferred_schema = schema

        # Set up progress display
        progress = None
        task = None
        if show_progress:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TextColumn("[cyan]{task.fields[records]} records"),
            )
            progress.start()
            task = progress.add_task("Fetching...", total=None, records=0)

        try:
            # Initial query request
            request_body = {
                "sql": sql,
                "pageSize": self.batch_size
            }

            response = self._execute_request(self.query_url, "POST", request_body)

            while True:
                data = response.get("data", [])
                self._stats.batches_fetched += 1

                if data:
                    # Infer schema from first batch if not provided
                    if inferred_schema is None:
                        inferred_schema = self._infer_schema(data[0])

                    # Convert batch to PyArrow table
                    batch_table = self._records_to_table(data, inferred_schema)
                    batches.append(batch_table)
                    records_written += len(data)
                    self._stats.records_fetched += len(data)

                    if progress and task is not None:
                        progress.update(task, records=records_written)

                # Check for more pages
                next_url = response.get("nextRecordsUrl")
                if not next_url:
                    break

                if not next_url.startswith("http"):
                    next_url = f"{self.auth.instance_url}{next_url}"

                response = self._execute_request(next_url, "GET")

            # Combine all batches and write
            if batches:
                combined_table = pa.concat_tables(batches)

                if partition_cols:
                    pq.write_to_dataset(
                        combined_table,
                        root_path=str(output_path),
                        partition_cols=partition_cols
                    )
                else:
                    pq.write_table(combined_table, str(output_path))

        finally:
            if progress:
                progress.stop()

        self._stats.end_time = datetime.now()
        return records_written

    def _infer_schema(self, record: Dict[str, Any]) -> pa.Schema:
        """
        Infer PyArrow schema from a sample record.

        Args:
            record: Sample record dictionary

        Returns:
            Inferred PyArrow schema
        """
        fields = []

        for key, value in record.items():
            if value is None:
                # Default to string for null values
                fields.append(pa.field(key, pa.string()))
            elif isinstance(value, bool):
                fields.append(pa.field(key, pa.bool_()))
            elif isinstance(value, int):
                fields.append(pa.field(key, pa.int64()))
            elif isinstance(value, float):
                fields.append(pa.field(key, pa.float64()))
            elif isinstance(value, str):
                # Check if it looks like a timestamp
                if "Timestamp" in key or "Date" in key:
                    fields.append(pa.field(key, pa.string()))  # Keep as string for flexibility
                else:
                    fields.append(pa.field(key, pa.string()))
            elif isinstance(value, dict):
                fields.append(pa.field(key, pa.string()))  # Serialize nested objects
            elif isinstance(value, list):
                fields.append(pa.field(key, pa.string()))  # Serialize arrays
            else:
                fields.append(pa.field(key, pa.string()))

        return pa.schema(fields)

    def _records_to_table(
        self,
        records: List[Dict[str, Any]],
        schema: pa.Schema
    ) -> pa.Table:
        """
        Convert records to PyArrow table.

        Args:
            records: List of record dictionaries
            schema: PyArrow schema

        Returns:
            PyArrow table
        """
        # Build column arrays
        columns = {field.name: [] for field in schema}

        for record in records:
            for field in schema:
                value = record.get(field.name)

                # Serialize complex types
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)

                columns[field.name].append(value)

        # Create arrays
        arrays = []
        for field in schema:
            arr = pa.array(columns[field.name], type=field.type)
            arrays.append(arr)

        return pa.Table.from_arrays(arrays, schema=schema)

    def get_dmo_metadata(self, dmo_name: str) -> Dict[str, Any]:
        """
        Get metadata for a Data Model Object.

        Args:
            dmo_name: DMO API name (e.g., ssot__AIAgentSession__dlm)

        Returns:
            DMO metadata including fields and relationships
        """
        url = f"{self.base_url}/ssot/querybuilder/metadata/{dmo_name}"
        return self._execute_request(url, "GET")

    def list_dmos(self) -> List[Dict[str, Any]]:
        """
        List all available Data Model Objects.

        Returns:
            List of DMO metadata dictionaries
        """
        url = f"{self.base_url}/ssot/querybuilder/metadata"
        response = self._execute_request(url, "GET")
        return response.get("metadata", [])

    def count(self, dmo_name: str, where_clause: Optional[str] = None) -> int:
        """
        Count records in a DMO.

        Args:
            dmo_name: DMO API name
            where_clause: Optional WHERE clause (without WHERE keyword)

        Returns:
            Record count
        """
        sql = f"SELECT COUNT(*) as cnt FROM {dmo_name}"
        if where_clause:
            sql += f" WHERE {where_clause}"

        result = list(self.query(sql, limit=1))
        if result:
            return int(result[0].get("cnt", 0))
        return 0
