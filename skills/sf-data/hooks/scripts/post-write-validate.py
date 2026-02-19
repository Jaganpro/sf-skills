#!/usr/bin/env python3
"""
sf-data Post-Write Validation Hook
===================================

Validates data operation files after they are written:
- .apex files: Anonymous Apex scripts for data operations
- .soql files: SOQL query files
- .csv files: Bulk import CSV files
- .json files: sObject tree JSON files

This hook is ADVISORY - it provides feedback but does not block writes.
"""

import json
import sys
import os
from pathlib import Path

# Add shared modules path
SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent  # sf-data/
SKILLS_ROOT = PLUGIN_ROOT.parent  # sf-skills/
SHARED_DIR = SKILLS_ROOT / "shared"
sys.path.insert(0, str(SHARED_DIR))

def main():
    """Main entry point for the validation hook."""
    try:
        # Read tool input from stdin
        input_data = json.load(sys.stdin)

        tool_input = input_data.get('tool_input', {})
        file_path = tool_input.get('file_path', '')

        if not file_path:
            # No file path provided, skip validation
            return

        # Determine file type and validate
        path = Path(file_path)
        extension = path.suffix.lower()

        # Only validate data-related files
        if extension not in ['.apex', '.soql', '.csv', '.json']:
            return

        # Check if file is in sf-data templates or user's data scripts
        if not is_data_file(file_path):
            return

        # Import the appropriate validator
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))

        from validate_data_operation import DataOperationValidator

        # Run validation
        validator = DataOperationValidator(file_path)
        result = validator.validate()

        # Add live query plan analysis for .soql files
        live_plan_result = None
        if extension == '.soql':
            live_plan_result = run_live_plan_analysis(file_path)

        # Output validation report
        if result:
            output = {
                'output': format_validation_report(result, live_plan_result)
            }
            print(json.dumps(output))

    except Exception as e:
        # Log error but don't block the write
        error_output = {
            'output': f'⚠️ Validation skipped: {str(e)}'
        }
        print(json.dumps(error_output))


def run_live_plan_analysis(file_path: str) -> dict:
    """
    Run live query plan analysis for SOQL files.

    Args:
        file_path: Path to .soql file

    Returns:
        dict with live plan results or None
    """
    try:
        from code_analyzer.live_query_plan import LiveQueryPlanAnalyzer

        # Read file content
        with open(file_path, 'r') as f:
            query = f.read().strip()

        if not query:
            return None

        analyzer = LiveQueryPlanAnalyzer()
        if not analyzer.is_org_available():
            return {'available': False, 'org': None}

        org_name = analyzer.get_target_org()
        plan_result = analyzer.analyze(query)

        return {
            'available': True,
            'org': org_name,
            'plan': plan_result,
            'suggestions': analyzer.get_optimization_suggestions(plan_result) if plan_result.success else []
        }

    except ImportError:
        return None
    except Exception:
        return None

def is_data_file(file_path: str) -> bool:
    """Check if the file is a data operation file that should be validated."""
    path = Path(file_path)

    # Check if it's in sf-data templates
    if 'sf-data' in str(path) and 'templates' in str(path):
        return True

    # Check if it's a data script based on naming patterns
    name_lower = path.stem.lower()
    data_patterns = [
        'factory', 'bulk', 'insert', 'update', 'delete', 'upsert',
        'import', 'export', 'cleanup', 'test', 'data', 'query'
    ]

    for pattern in data_patterns:
        if pattern in name_lower:
            return True

    # Check file extension for SOQL files
    if path.suffix.lower() == '.soql':
        return True

    return False

def format_validation_report(result: dict, live_plan_result: dict = None) -> str:
    """Format the validation result as a readable report."""
    lines = []

    # Header
    score = result.get('score', 0)
    max_score = result.get('max_score', 130)
    rating = get_rating(score, max_score)

    lines.append('═' * 60)
    lines.append(f'   sf-data Validation Report')
    lines.append('═' * 60)
    lines.append('')
    lines.append(f'🎯 Score: {score}/{max_score} {rating}')
    lines.append('')

    # Category breakdown
    categories = result.get('categories', {})
    if categories:
        lines.append('Category Breakdown:')
        lines.append('─' * 60)
        for cat_name, cat_data in categories.items():
            cat_score = cat_data.get('score', 0)
            cat_max = cat_data.get('max', 0)
            pct = (cat_score / cat_max * 100) if cat_max > 0 else 0
            status = '✅' if pct >= 80 else '⚠️' if pct >= 60 else '❌'
            lines.append(f'{status} {cat_name}: {cat_score}/{cat_max} ({pct:.0f}%)')
        lines.append('')

    # Live Query Plan Analysis (if available)
    if live_plan_result:
        lines.append('🌐 Live Query Plan Analysis')
        lines.append('─' * 60)

        if not live_plan_result.get('available'):
            lines.append('   ⚠️ No org connected - run: sf org login web')
        elif live_plan_result.get('plan'):
            plan = live_plan_result['plan']
            org = live_plan_result.get('org', 'unknown')
            lines.append(f'   Org: {org}')

            if plan.success:
                lines.append(f'   {plan.icon} Selective: {plan.is_selective}')
                lines.append(f'   📊 Relative Cost: {plan.relative_cost:.2f} ({plan.selectivity_rating})')
                lines.append(f'   📈 Operation: {plan.leading_operation}')

                if plan.cardinality > 0:
                    lines.append(f'   📋 Cardinality: {plan.cardinality:,} / {plan.sobject_cardinality:,}')

                if plan.notes:
                    lines.append('')
                    lines.append('   📝 Query Plan Notes:')
                    for note in plan.notes[:3]:
                        lines.append(f'      • {str(note)[:55]}')

                # Add suggestions to recommendations
                suggestions = live_plan_result.get('suggestions', [])
                if suggestions:
                    lines.append('')
                    lines.append('   💡 Optimization Suggestions:')
                    for sug in suggestions[:3]:
                        lines.append(f'      • {sug[:55]}')
            else:
                lines.append(f'   ❌ Error: {plan.error[:50]}')

        lines.append('')

    # Issues
    issues = result.get('issues', [])
    if issues:
        lines.append('Issues Found:')
        lines.append('─' * 60)
        for issue in issues[:10]:  # Limit to 10 issues
            severity = issue.get('severity', 'warning')
            icon = '❌' if severity == 'error' else '⚠️' if severity == 'warning' else 'ℹ️'
            category = issue.get('category', 'General')
            message = issue.get('message', 'Unknown issue')
            lines.append(f'{icon} [{category}] {message}')
        if len(issues) > 10:
            lines.append(f'   ... and {len(issues) - 10} more issues')
        lines.append('')

    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        lines.append('Recommendations:')
        lines.append('─' * 60)
        for rec in recommendations[:5]:
            lines.append(f'💡 {rec}')
        lines.append('')

    lines.append('═' * 60)

    # Status
    if score >= max_score * 0.9:
        lines.append('✅ VALIDATION PASSED - Excellent!')
    elif score >= max_score * 0.7:
        lines.append('✅ VALIDATION PASSED - Good')
    elif score >= max_score * 0.5:
        lines.append('⚠️ VALIDATION PASSED - Review recommended')
    else:
        lines.append('⚠️ VALIDATION PASSED (Advisory) - Please review issues')

    lines.append('═' * 60)

    return '\n'.join(lines)

def get_rating(score: int, max_score: int) -> str:
    """Get star rating based on score percentage."""
    pct = (score / max_score * 100) if max_score > 0 else 0

    if pct >= 90:
        return '⭐⭐⭐⭐⭐ Excellent'
    elif pct >= 80:
        return '⭐⭐⭐⭐ Very Good'
    elif pct >= 70:
        return '⭐⭐⭐ Good'
    elif pct >= 60:
        return '⭐⭐ Needs Work'
    else:
        return '⭐ Critical Issues'

if __name__ == '__main__':
    main()
