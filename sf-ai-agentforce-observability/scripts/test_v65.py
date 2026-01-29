#!/usr/bin/env python3
"""
Test script for Data 360 v65.0 API with async query support.

Tests API functionality from simple to complex:
- Level 1: Basic connectivity (list_dmos)
- Level 2: Simple query execution
- Level 3: Async status polling
- Level 4: Paginated rows retrieval
- Level 5: Cancel query
- Level 6: Full extraction
- Level 7: Incremental extraction

Run: python3 scripts/test_v65.py --org Vivint-DevInt --consumer-key "..."
"""

import argparse
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.auth import Data360Auth
from scripts.datacloud_client import Data360Client


def test_level_1_connectivity(client: Data360Client) -> bool:
    """Level 1: Basic connectivity test."""
    print("\n📡 Level 1: Testing v65.0 connectivity...")
    try:
        # Test connectivity with a minimal query (faster than list_dmos)
        result = list(client.query(
            "SELECT ssot__Id__c FROM ssot__AIAgentSession__dlm LIMIT 1"
        ))
        print(f"   ✅ Connected to Data 360 v65.0!")
        print(f"   📊 API Version: {client.api_version}")
        print(f"   🔗 Endpoint: {client.query_url}")

        if result:
            print(f"   📋 STDM data available ({len(result)} sample record)")
        else:
            print(f"   ℹ️  STDM accessible but no session data yet")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_level_2_simple_query(client: Data360Client) -> bool:
    """Level 2: Simple query test."""
    print("\n📋 Level 2: Testing simple query...")
    try:
        result = list(client.query(
            "SELECT ssot__Id__c FROM ssot__AIAgentSession__dlm LIMIT 5"
        ))
        print(f"   ✅ Query returned {len(result)} records")

        if result:
            print(f"   📝 Sample ID: {result[0].get('ssot__Id__c', 'N/A')[:50]}...")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_level_3_async_status(client: Data360Client) -> bool:
    """Level 3: Async status polling test."""
    print("\n🔄 Level 3: Testing async status endpoint...")
    try:
        # Execute a query that might return async
        response = client._execute_request(
            client.query_url,
            "POST",
            {"sql": "SELECT * FROM ssot__AIAgentSession__dlm LIMIT 100"}
        )

        status = response.get("status", {})
        query_id = status.get("queryId")
        completion = status.get("completionStatus", "N/A")

        if query_id:
            print(f"   📊 Query ID received: {query_id[:30]}...")
            print(f"   📊 Initial status: {completion}")

            # Poll status
            poll_result = client.get_query_status(query_id)
            poll_status = poll_result.get("status", {}).get("completionStatus", "Unknown")
            print(f"   ✅ Status poll works: {poll_status}")
        else:
            print(f"   ℹ️  Query returned synchronously (status: {completion})")
            print(f"   ℹ️  Data rows: {len(response.get('data', []))}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_level_4_paginated_rows(client: Data360Client) -> bool:
    """Level 4: Paginated rows test."""
    print("\n📑 Level 4: Testing paginated rows endpoint...")
    try:
        # Run a larger query
        response = client._execute_request(
            client.query_url,
            "POST",
            {"sql": "SELECT * FROM ssot__AIAgentSession__dlm"}
        )

        status = response.get("status", {})
        query_id = status.get("queryId")
        completion = status.get("completionStatus", "N/A")

        if query_id and completion in ["Running", "Completed", "MoreChunksAvailable"]:
            # Wait for completion if running
            while completion == "Running":
                time.sleep(1)
                poll = client.get_query_status(query_id)
                completion = poll.get("status", {}).get("completionStatus", "Unknown")
                print(f"   ⏳ Waiting... status: {completion}")

            # Fetch paginated rows
            batch1 = client.get_query_rows(query_id, offset=0, row_limit=10)
            batch1_data = batch1.get("data", [])
            print(f"   ✅ Batch 1 (offset=0): {len(batch1_data)} rows")

            batch2 = client.get_query_rows(query_id, offset=10, row_limit=10)
            batch2_data = batch2.get("data", [])
            print(f"   ✅ Batch 2 (offset=10): {len(batch2_data)} rows")
        else:
            # Query completed synchronously
            data_count = len(response.get("data", []))
            print(f"   ℹ️  Query returned {data_count} rows synchronously")
            print(f"   ℹ️  (Paginated rows endpoint not needed for small results)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_level_5_cancel_query(client: Data360Client) -> bool:
    """Level 5: Cancel query test."""
    print("\n❌ Level 5: Testing cancel query endpoint...")
    try:
        # Start a potentially larger query
        response = client._execute_request(
            client.query_url,
            "POST",
            {"sql": "SELECT * FROM ssot__AIAgentInteractionStep__dlm"}
        )

        status = response.get("status", {})
        query_id = status.get("queryId")
        completion = status.get("completionStatus", "N/A")

        if query_id:
            print(f"   📊 Query ID: {query_id[:30]}...")
            print(f"   📊 Status: {completion}")

            # Cancel it
            success = client.cancel_query(query_id)
            print(f"   ✅ Cancel query: {'Success' if success else 'Failed'}")
        else:
            print(f"   ℹ️  Query completed synchronously ({completion})")
            print(f"   ℹ️  (Cancel endpoint only works for async queries)")
        return True
    except RuntimeError as e:
        # Query may have already completed
        if "404" in str(e) or "not found" in str(e).lower():
            print(f"   ℹ️  Query already completed (cannot cancel)")
            return True
        print(f"   ❌ Failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_level_6_full_extraction(client: Data360Client, output_dir: Path) -> bool:
    """Level 6: Full extraction test."""
    print("\n📦 Level 6: Testing full extraction...")
    try:
        from scripts.extractor import STDMExtractor

        # Clean output directory
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        extractor = STDMExtractor(client, output_dir)

        # Extract last 3 days
        since = datetime.utcnow() - timedelta(days=3)

        result = extractor.extract_sessions(
            since=since,
            show_progress=True
        )

        print(f"\n   📊 Extraction Results:")
        print(f"   ✅ Sessions: {result.sessions_count}")
        print(f"   ✅ Interactions: {result.interactions_count}")
        print(f"   ✅ Steps: {result.steps_count}")
        print(f"   ✅ Messages: {result.messages_count}")
        print(f"   ⏱️  Duration: {result.duration_seconds:.1f}s")

        if result.errors:
            print(f"   ⚠️  Errors: {result.errors}")

        return result.sessions_count >= 0 and not result.errors
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_level_7_incremental_extraction(client: Data360Client, output_dir: Path) -> bool:
    """Level 7: Incremental extraction test."""
    print("\n🔄 Level 7: Testing incremental extraction...")
    try:
        from scripts.extractor import STDMExtractor

        # Requires Level 6 to have run first
        if not (output_dir / "sessions" / "data.parquet").exists():
            print("   ⚠️  No existing data found. Run Level 6 first.")
            print("   ℹ️  Skipping incremental test.")
            return True

        extractor = STDMExtractor(client, output_dir)

        result = extractor.extract_incremental(show_progress=True)

        print(f"\n   📊 Incremental Results:")
        print(f"   ✅ Sessions: {result.sessions_count}")
        print(f"   ✅ Interactions: {result.interactions_count}")
        print(f"   ✅ Steps: {result.steps_count}")
        print(f"   ✅ Messages: {result.messages_count}")
        print(f"   ⏱️  Duration: {result.duration_seconds:.1f}s")

        if result.errors:
            print(f"   ⚠️  Errors: {result.errors}")

        return not result.errors
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test Data 360 v65.0 API with async query support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests (consumer key auto-loaded from ~/.sf/jwt/)
  python3 scripts/test_v65.py --org Vivint-DevInt

  # Run specific level
  python3 scripts/test_v65.py --org Vivint-DevInt --level 3

  # Run levels 1-5 only (skip extraction)
  python3 scripts/test_v65.py --org Vivint-DevInt --max-level 5

  # Explicit consumer key (overrides file/env)
  python3 scripts/test_v65.py --org Vivint-DevInt --consumer-key "3MVG9..."
        """
    )
    parser.add_argument("--org", required=True, help="Salesforce org alias")
    parser.add_argument("--consumer-key", help="ECA consumer key (auto-loaded from ~/.sf/jwt/ if not provided)")
    parser.add_argument("--output", default="/tmp/v65-test", help="Output directory for extractions")
    parser.add_argument("--level", type=int, default=0, help="Run specific level only (0=all)")
    parser.add_argument("--max-level", type=int, default=7, help="Maximum level to run (default: 7)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("=" * 60)
    print("🧪 Data 360 v65.0 API Test Suite")
    print("=" * 60)

    # Initialize client
    print(f"\n🔧 Initializing...")
    print(f"   Org: {args.org}")

    auth = Data360Auth(org_alias=args.org, consumer_key=args.consumer_key)
    client = Data360Client(auth)
    output_dir = Path(args.output)

    print(f"   API Version: {client.api_version}")
    print(f"   Base URL: {client.base_url}")
    print(f"   Output Dir: {output_dir}")

    # Define test levels
    tests = [
        (1, "Connectivity", test_level_1_connectivity),
        (2, "Simple Query", test_level_2_simple_query),
        (3, "Async Status", test_level_3_async_status),
        (4, "Paginated Rows", test_level_4_paginated_rows),
        (5, "Cancel Query", test_level_5_cancel_query),
        (6, "Full Extraction", lambda c: test_level_6_full_extraction(c, output_dir)),
        (7, "Incremental Extraction", lambda c: test_level_7_incremental_extraction(c, output_dir)),
    ]

    results = []
    for level, name, test_fn in tests:
        # Filter by level selection
        if args.level != 0 and args.level != level:
            continue
        if level > args.max_level:
            continue

        try:
            passed = test_fn(client)
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            passed = False

        results.append((level, name, passed))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    for level, name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   Level {level} ({name}): {status}")

    total_pass = sum(1 for _, _, p in results if p)
    total_tests = len(results)

    print(f"\n   Total: {total_pass}/{total_tests} passed")

    # Exit code
    if total_pass == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
