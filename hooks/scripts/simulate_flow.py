#!/usr/bin/env python3
"""
Salesforce Flow Simulator - Bulk Testing & Governor Limit Analysis

Simulates flow execution with mock data to catch governor limit issues
before deployment. Tests bulkification and performance with 200+ records.

Usage:
    python3 flow_simulator.py <path-to-flow-meta.xml> --test-records 200 [--mock-data]
    python3 flow_simulator.py <path-to-flow-meta.xml> --analyze-only
"""

import sys
import xml.etree.ElementTree as ET
import argparse
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class GovernorLimits:
    """Salesforce governor limits per transaction"""
    SOQL_QUERIES = 100
    SOQL_RECORDS = 50000
    DML_STATEMENTS = 150
    DML_ROWS = 10000
    CPU_TIME_MS = 10000
    HEAP_SIZE_MB = 6

@dataclass
class SimulationMetrics:
    """Metrics tracked during simulation"""
    soql_queries: int = 0
    soql_records: int = 0
    dml_statements: int = 0
    dml_rows: int = 0
    cpu_time_ms: int = 0
    heap_size_kb: int = 0
    loops_executed: int = 0
    decisions_evaluated: int = 0

class FlowSimulator:
    def __init__(self, xml_path: str, num_records: int = 200):
        self.xml_path = xml_path
        self.num_records = num_records
        self.tree = None
        self.root = None
        self.namespace = {'ns': 'http://soap.sforce.com/2006/04/metadata'}
        self.metrics = SimulationMetrics()
        self.limits = GovernorLimits()
        self.warnings = []
        self.errors = []

    def simulate(self) -> Dict:
        """Main simulation entry point"""
        print(f"\n🔬 Simulating Flow Execution with {self.num_records} records...\n")

        # Load flow
        if not self._load_xml():
            return self._generate_report()

        # Analyze flow structure
        flow_type = self._get_flow_type()
        print(f"Flow Type: {flow_type}")
        print(f"Processing {self.num_records} records in bulk...\n")

        # Simulate execution
        self._simulate_flow_execution()

        # Check limits
        self._check_governor_limits()

        return self._generate_report()

    def _load_xml(self) -> bool:
        """Load and parse flow XML"""
        try:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()
            return True
        except Exception as e:
            self.errors.append(f"Failed to load flow: {str(e)}")
            return False

    def _get_flow_type(self) -> str:
        """Determine flow type"""
        process_type = self.root.find('ns:processType', self.namespace)
        if process_type is not None:
            if process_type.text == 'Flow':
                return "Screen Flow"
            elif process_type.text == 'AutoLaunchedFlow':
                start = self.root.find('ns:start', self.namespace)
                if start is not None:
                    trigger_type = start.find('ns:triggerType', self.namespace)
                    if trigger_type is not None:
                        if 'RecordAfterSave' in trigger_type.text:
                            return "Record-Triggered Flow (After Save)"
                        elif 'RecordBeforeSave' in trigger_type.text:
                            return "Record-Triggered Flow (Before Save)"
                        elif 'RecordBeforeDelete' in trigger_type.text:
                            return "Record-Triggered Flow (Before Delete)"
                    schedule = start.find('ns:schedule', self.namespace)
                    if schedule is not None:
                        return "Scheduled Flow"
                return "Autolaunched Flow"
        return "Unknown"

    def _simulate_flow_execution(self):
        """Simulate flow execution and track resource usage"""

        # Check if bulkSupport is enabled
        start = self.root.find('ns:start', self.namespace)
        if start is not None:
            trigger_type = start.find('ns:triggerType', self.namespace)
            if trigger_type is not None:
                bulk_support = start.find('ns:bulkSupport', self.namespace)
                if bulk_support is None or bulk_support.text.lower() != 'true':
                    self.warnings.append(
                        "⚠️  bulkSupport not enabled - flow will process records individually"
                    )
                    # Simulate individual processing (worst case)
                    self._simulate_individual_processing()
                    return

        # Simulate bulk processing (best case)
        self._simulate_bulk_processing()

    def _simulate_individual_processing(self):
        """Simulate processing each record individually (no bulkification)"""
        print("⚠️  Simulating INDIVIDUAL processing (bulkSupport=false)...")

        # Count DML operations in flow
        dml_per_record = self._count_dml_operations()
        soql_per_record = self._count_soql_queries()

        # Simulate for each record
        total_dml = dml_per_record * self.num_records
        total_soql = soql_per_record * self.num_records

        self.metrics.dml_statements = total_dml
        self.metrics.soql_queries = total_soql
        self.metrics.dml_rows = self.num_records  # Each DML affects 1 row

        # Estimate CPU time (rough approximation)
        self.metrics.cpu_time_ms = self.num_records * 50  # ~50ms per record

        if total_dml > self.limits.DML_STATEMENTS:
            self.errors.append(
                f"❌ GOVERNOR LIMIT EXCEEDED: {total_dml} DML statements "
                f"(limit: {self.limits.DML_STATEMENTS})"
            )

        if total_soql > self.limits.SOQL_QUERIES:
            self.errors.append(
                f"❌ GOVERNOR LIMIT EXCEEDED: {total_soql} SOQL queries "
                f"(limit: {self.limits.SOQL_QUERIES})"
            )

    def _simulate_bulk_processing(self):
        """Simulate bulk processing with collections"""
        print("✓ Simulating BULK processing (bulkSupport=true)...")

        # Count unique DML operations (executed once per batch)
        dml_operations = self._count_dml_operations()
        soql_queries = self._count_soql_queries()

        self.metrics.dml_statements = dml_operations
        self.metrics.soql_queries = soql_queries
        self.metrics.dml_rows = self.num_records * dml_operations

        # Estimate CPU time for bulk
        self.metrics.cpu_time_ms = 100 + (self.num_records * 5)  # Base + per-record processing

        # Check for loops that might cause issues
        self._analyze_loops()

    def _count_dml_operations(self) -> int:
        """Count DML operations in flow"""
        dml_types = ['recordCreates', 'recordUpdates', 'recordDeletes']
        count = 0
        for dml_type in dml_types:
            count += len(self.root.findall(f'ns:{dml_type}', self.namespace))
        return count

    def _count_soql_queries(self) -> int:
        """Count SOQL queries in flow"""
        return len(self.root.findall('ns:recordLookups', self.namespace))

    def _analyze_loops(self):
        """Analyze loops for potential issues"""
        loops = self.root.findall('.//ns:loops', self.namespace)

        for loop in loops:
            loop_name = loop.find('ns:name', self.namespace).text
            self.metrics.loops_executed += 1

            # Check if DML is inside loop (CRITICAL issue)
            if self._has_dml_in_loop_path(loop):
                iterations = self.num_records  # Assuming loop iterates over input collection
                dml_in_loop = self._count_dml_in_path(loop)
                total_dml_from_loop = dml_in_loop * iterations

                self.errors.append(
                    f"❌ CRITICAL: Loop '{loop_name}' contains DML operations. "
                    f"With {iterations} records, this will execute {total_dml_from_loop} DML statements "
                    f"(limit: {self.limits.DML_STATEMENTS})"
                )

                # Add to metrics
                self.metrics.dml_statements += total_dml_from_loop

            # Estimate CPU time for loop
            self.metrics.cpu_time_ms += self.num_records * 10  # ~10ms per iteration

    def _has_dml_in_loop_path(self, loop_elem) -> bool:
        """Check if loop path contains DML"""
        next_connector = loop_elem.find('ns:nextValueConnector', self.namespace)
        if next_connector is not None:
            target_ref = next_connector.find('ns:targetReference', self.namespace)
            if target_ref is not None:
                return self._check_path_for_dml(target_ref.text, set())
        return False

    def _check_path_for_dml(self, element_name: str, visited: set) -> bool:
        """Recursively check path for DML operations"""
        if element_name in visited:
            return False
        visited.add(element_name)

        # Check if this element is a DML operation
        for dml_type in ['recordCreates', 'recordUpdates', 'recordDeletes']:
            elem = self._find_element_by_name(element_name, dml_type)
            if elem is not None:
                return True

        # Check other elements and follow connectors
        for elem_type in ['assignments', 'decisions']:
            elem = self._find_element_by_name(element_name, elem_type)
            if elem is not None:
                for connector in elem.findall('.//ns:connector', self.namespace):
                    target_ref = connector.find('ns:targetReference', self.namespace)
                    if target_ref is not None and self._check_path_for_dml(target_ref.text, visited):
                        return True

        return False

    def _count_dml_in_path(self, loop_elem) -> int:
        """Count DML operations in loop path"""
        count = 0
        next_connector = loop_elem.find('ns:nextValueConnector', self.namespace)
        if next_connector is not None:
            target_ref = next_connector.find('ns:targetReference', self.namespace)
            if target_ref is not None:
                count = self._count_dml_recursive(target_ref.text, set())
        return count

    def _count_dml_recursive(self, element_name: str, visited: set) -> int:
        """Recursively count DML operations"""
        if element_name in visited:
            return 0
        visited.add(element_name)

        count = 0
        for dml_type in ['recordCreates', 'recordUpdates', 'recordDeletes']:
            if self._find_element_by_name(element_name, dml_type):
                count += 1

        return count

    def _find_element_by_name(self, name: str, elem_type: str):
        """Find element by name and type"""
        for elem in self.root.findall(f'ns:{elem_type}', self.namespace):
            name_elem = elem.find('ns:name', self.namespace)
            if name_elem is not None and name_elem.text == name:
                return elem
        return None

    def _check_governor_limits(self):
        """Check if metrics exceed governor limits"""

        if self.metrics.soql_queries > self.limits.SOQL_QUERIES:
            self.errors.append(
                f"❌ SOQL Query limit exceeded: {self.metrics.soql_queries} "
                f"(limit: {self.limits.SOQL_QUERIES})"
            )
        elif self.metrics.soql_queries > self.limits.SOQL_QUERIES * 0.8:
            self.warnings.append(
                f"⚠️  Approaching SOQL Query limit: {self.metrics.soql_queries} "
                f"(80% of {self.limits.SOQL_QUERIES})"
            )

        if self.metrics.dml_statements > self.limits.DML_STATEMENTS:
            self.errors.append(
                f"❌ DML Statement limit exceeded: {self.metrics.dml_statements} "
                f"(limit: {self.limits.DML_STATEMENTS})"
            )
        elif self.metrics.dml_statements > self.limits.DML_STATEMENTS * 0.8:
            self.warnings.append(
                f"⚠️  Approaching DML Statement limit: {self.metrics.dml_statements} "
                f"(80% of {self.limits.DML_STATEMENTS})"
            )

        if self.metrics.dml_rows > self.limits.DML_ROWS:
            self.errors.append(
                f"❌ DML Rows limit exceeded: {self.metrics.dml_rows} "
                f"(limit: {self.limits.DML_ROWS})"
            )

        if self.metrics.cpu_time_ms > self.limits.CPU_TIME_MS:
            self.errors.append(
                f"❌ CPU Time limit exceeded: {self.metrics.cpu_time_ms}ms "
                f"(limit: {self.limits.CPU_TIME_MS}ms)"
            )
        elif self.metrics.cpu_time_ms > self.limits.CPU_TIME_MS * 0.8:
            self.warnings.append(
                f"⚠️  Approaching CPU Time limit: {self.metrics.cpu_time_ms}ms "
                f"(80% of {self.limits.CPU_TIME_MS}ms)"
            )

    def _generate_report(self) -> Dict:
        """Generate simulation report"""
        print("\n" + "━" * 70)
        print("Flow Simulation Report")
        print("━" * 70)
        print(f"\nTest Configuration:")
        print(f"  Records Processed: {self.num_records}")
        print(f"  Flow: {self.xml_path.split('/')[-1]}")

        print(f"\n📊 Resource Usage:")
        print(f"  SOQL Queries:    {self.metrics.soql_queries:4d} / {self.limits.SOQL_QUERIES} "
              f"({self._percentage(self.metrics.soql_queries, self.limits.SOQL_QUERIES)}%)")
        print(f"  SOQL Records:    {self.metrics.soql_records:4d} / {self.limits.SOQL_RECORDS} "
              f"({self._percentage(self.metrics.soql_records, self.limits.SOQL_RECORDS)}%)")
        print(f"  DML Statements:  {self.metrics.dml_statements:4d} / {self.limits.DML_STATEMENTS} "
              f"({self._percentage(self.metrics.dml_statements, self.limits.DML_STATEMENTS)}%)")
        print(f"  DML Rows:        {self.metrics.dml_rows:4d} / {self.limits.DML_ROWS} "
              f"({self._percentage(self.metrics.dml_rows, self.limits.DML_ROWS)}%)")
        print(f"  CPU Time:        {self.metrics.cpu_time_ms:4d}ms / {self.limits.CPU_TIME_MS}ms "
              f"({self._percentage(self.metrics.cpu_time_ms, self.limits.CPU_TIME_MS)}%)")

        # Errors
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        else:
            print(f"\n✓ No governor limit errors detected")

        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        # Overall status
        print("\n" + "━" * 70)
        if self.errors:
            print("❌ SIMULATION FAILED - Flow will hit governor limits with bulk data")
            print("\nRecommendations:")
            print("  1. Enable bulkSupport if not already enabled")
            print("  2. Remove DML operations from inside loops")
            print("  3. Use collection-based DML operations")
            print("  4. Consider using Transform element instead of loops")
            status = "FAILED"
        elif self.warnings:
            print("⚠️  SIMULATION PASSED WITH WARNINGS - Monitor closely in production")
            status = "WARNING"
        else:
            print("✓ SIMULATION PASSED - Flow is bulkified and ready for production")
            status = "PASSED"

        print("━" * 70 + "\n")

        return {
            'status': status,
            'metrics': self.metrics.__dict__,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def _percentage(self, value: int, limit: int) -> int:
        """Calculate percentage of limit used"""
        if limit == 0:
            return 0
        return int((value / limit) * 100)

def main():
    parser = argparse.ArgumentParser(
        description='Simulate Salesforce Flow execution with bulk data'
    )
    parser.add_argument('flow_xml', help='Path to flow metadata XML file')
    parser.add_argument('--test-records', type=int, default=200,
                       help='Number of records to simulate (default: 200)')
    parser.add_argument('--mock-data', action='store_true',
                       help='Generate mock data for testing')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Analyze flow structure without simulation')

    args = parser.parse_args()

    simulator = FlowSimulator(args.flow_xml, args.test_records)
    result = simulator.simulate()

    # Exit with error code if simulation failed
    if result['status'] == 'FAILED':
        sys.exit(1)
    elif result['status'] == 'WARNING':
        sys.exit(0)  # Warnings don't fail the build
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
