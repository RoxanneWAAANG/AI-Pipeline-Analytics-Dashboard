#!/usr/bin/env python3
"""
Comprehensive Test Coverage Report Generator
Generates detailed coverage reports with metrics and analysis
"""

import subprocess
import sys
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

def run_command(command, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None

def generate_coverage_report():
    """Generate comprehensive test coverage report"""
    print("🧪 Generating Comprehensive Test Coverage Report")
    print("=" * 60)
    
    # Run tests with coverage
    print("📊 Running tests with coverage analysis...")
    
    coverage_cmd = (
        "python -m pytest tests/ -v "
        "--cov=analytics_dashboard "
        "--cov-report=html:htmlcov "
        "--cov-report=xml:coverage.xml "
        "--cov-report=json:coverage.json "
        "--cov-report=term-missing "
        "--cov-fail-under=80"
    )
    
    print(f"Running: {coverage_cmd}")
    result = run_command(coverage_cmd, capture_output=False)
    
    # Parse coverage results
    print("\n📈 Parsing coverage results...")
    coverage_data = parse_coverage_results()
    
    # Generate detailed report
    print("\n📝 Generating detailed report...")
    generate_detailed_report(coverage_data)
    
    # Generate performance metrics
    print("\n⚡ Running performance benchmarks...")
    run_performance_tests()
    
    print("\n✅ Coverage report generation complete!")
    print(f"📁 Reports available in: htmlcov/index.html")

def parse_coverage_results():
    """Parse coverage results from multiple formats"""
    coverage_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {},
        'files': {},
        'missing_lines': {}
    }
    
    # Parse XML coverage report
    if os.path.exists('coverage.xml'):
        try:
            tree = ET.parse('coverage.xml')
            root = tree.getroot()
            
            # Get overall coverage
            coverage_data['summary'] = {
                'line_rate': float(root.get('line-rate', 0)) * 100,
                'branch_rate': float(root.get('branch-rate', 0)) * 100,
                'lines_covered': int(root.get('lines-covered', 0)),
                'lines_valid': int(root.get('lines-valid', 0)),
                'branches_covered': int(root.get('branches-covered', 0)),
                'branches_valid': int(root.get('branches-valid', 0))
            }
            
            # Get file-level coverage
            for package in root.findall('.//package'):
                for class_elem in package.findall('classes/class'):
                    filename = class_elem.get('filename', '')
                    if filename.endswith('.py'):
                        lines = class_elem.findall('lines/line')
                        covered_lines = sum(1 for line in lines if int(line.get('hits', 0)) > 0)
                        total_lines = len(lines)
                        
                        coverage_data['files'][filename] = {
                            'line_rate': (covered_lines / total_lines * 100) if total_lines > 0 else 0,
                            'lines_covered': covered_lines,
                            'lines_total': total_lines,
                            'missing_lines': [
                                int(line.get('number')) 
                                for line in lines 
                                if int(line.get('hits', 0)) == 0
                            ]
                        }
                        
        except Exception as e:
            print(f"Error parsing XML coverage: {e}")
    
    # Parse JSON coverage report (if available)
    if os.path.exists('coverage.json'):
        try:
            with open('coverage.json', 'r') as f:
                json_data = json.load(f)
                coverage_data['json_summary'] = json_data.get('totals', {})
        except Exception as e:
            print(f"Error parsing JSON coverage: {e}")
    
    return coverage_data

def generate_detailed_report(coverage_data):
    """Generate a detailed coverage report in markdown format"""
    report_content = f"""# Test Coverage Report

Generated: {coverage_data['timestamp']}

## Summary

| Metric | Value |
|--------|-------|
| Line Coverage | {coverage_data['summary'].get('line_rate', 0):.1f}% |
| Branch Coverage | {coverage_data['summary'].get('branch_rate', 0):.1f}% |
| Lines Covered | {coverage_data['summary'].get('lines_covered', 0)} |
| Total Lines | {coverage_data['summary'].get('lines_valid', 0)} |

## Coverage by File

"""
    
    # Add file-level coverage details
    for filename, file_data in coverage_data['files'].items():
        report_content += f"### {filename}\n\n"
        report_content += f"- **Coverage**: {file_data['line_rate']:.1f}%\n"
        report_content += f"- **Lines Covered**: {file_data['lines_covered']}/{file_data['lines_total']}\n"
        
        if file_data['missing_lines']:
            missing_str = ', '.join(map(str, file_data['missing_lines'][:10]))
            if len(file_data['missing_lines']) > 10:
                missing_str += f"... ({len(file_data['missing_lines'])} total)"
            report_content += f"- **Missing Lines**: {missing_str}\n"
        
        report_content += "\n"
    
    # Coverage quality assessment
    overall_coverage = coverage_data['summary'].get('line_rate', 0)
    
    report_content += "## Coverage Quality Assessment\n\n"
    
    if overall_coverage >= 90:
        report_content += "✅ **Excellent** - Coverage is excellent (≥90%)\n"
    elif overall_coverage >= 80:
        report_content += "✅ **Good** - Coverage meets requirements (≥80%)\n"
    elif overall_coverage >= 70:
        report_content += "⚠️ **Acceptable** - Coverage is acceptable but could be improved\n"
    else:
        report_content += "❌ **Poor** - Coverage is below recommended threshold\n"
    
    # Recommendations
    report_content += "\n## Recommendations\n\n"
    
    uncovered_files = [
        filename for filename, data in coverage_data['files'].items()
        if data['line_rate'] < 80
    ]
    
    if uncovered_files:
        report_content += "### Files needing attention:\n\n"
        for filename in uncovered_files:
            file_data = coverage_data['files'][filename]
            report_content += f"- `{filename}`: {file_data['line_rate']:.1f}% coverage\n"
    
    if overall_coverage < 80:
        report_content += "\n### Action items:\n\n"
        report_content += "- Add more unit tests for uncovered code paths\n"
        report_content += "- Focus on edge cases and error handling\n"
        report_content += "- Consider integration tests for complex workflows\n"
    
    # Save report
    with open('coverage_report.md', 'w') as f:
        f.write(report_content)
    
    print(f"📄 Detailed report saved to: coverage_report.md")

def run_performance_tests():
    """Run performance benchmark tests"""
    perf_cmd = "python -m pytest tests/test_performance.py -v -s --tb=short"
    
    print(f"Running: {perf_cmd}")
    result = run_command(perf_cmd, capture_output=False)
    
    if result is not None:
        print("✅ Performance tests completed")
    else:
        print("⚠️ Performance tests had issues")

def analyze_test_results():
    """Analyze test results and provide insights"""
    print("\n🔍 Analyzing test results...")
    
    # Count test files
    test_files = list(Path('tests').glob('test_*.py'))
    total_test_files = len(test_files)
    
    # Get line counts
    total_test_lines = 0
    for test_file in test_files:
        try:
            with open(test_file, 'r') as f:
                total_test_lines += len(f.readlines())
        except Exception:
            pass
    
    # Get source line counts
    source_files = ['analytics_dashboard.py', 'run_demo_dashboard.py']
    total_source_lines = 0
    for source_file in source_files:
        if os.path.exists(source_file):
            try:
                with open(source_file, 'r') as f:
                    total_source_lines += len(f.readlines())
            except Exception:
                pass
    
    # Calculate ratios
    test_to_code_ratio = (total_test_lines / total_source_lines) if total_source_lines > 0 else 0
    
    print(f"📊 Test Analysis:")
    print(f"   - Test files: {total_test_files}")
    print(f"   - Test lines: {total_test_lines}")
    print(f"   - Source lines: {total_source_lines}")
    print(f"   - Test/Code ratio: {test_to_code_ratio:.2f}")
    
    if test_to_code_ratio >= 0.5:
        print("   ✅ Good test coverage ratio")
    else:
        print("   ⚠️ Consider adding more tests")

def generate_badge_info():
    """Generate coverage badge information"""
    if os.path.exists('coverage.xml'):
        try:
            tree = ET.parse('coverage.xml')
            root = tree.getroot()
            coverage = float(root.get('line-rate', 0)) * 100
            
            # Determine badge color
            if coverage >= 90:
                color = 'brightgreen'
            elif coverage >= 80:
                color = 'green'
            elif coverage >= 70:
                color = 'yellow'
            else:
                color = 'red'
            
            badge_url = f"https://img.shields.io/badge/coverage-{coverage:.1f}%25-{color}"
            
            print(f"\n🏷️ Coverage Badge:")
            print(f"   Markdown: ![Coverage]({badge_url})")
            print(f"   URL: {badge_url}")
            
        except Exception as e:
            print(f"Error generating badge info: {e}")

def main():
    """Main function"""
    print("🚀 AI Pipeline Analytics - Test Coverage Analysis")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('analytics_dashboard.py'):
        print("❌ Error: analytics_dashboard.py not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if pytest is available
    if run_command("python -m pytest --version") is None:
        print("❌ Error: pytest not found")
        print("Please install pytest: pip install pytest pytest-cov")
        sys.exit(1)
    
    # Generate coverage report
    generate_coverage_report()
    
    # Analyze results
    analyze_test_results()
    
    # Generate badge info
    generate_badge_info()
    
    print("\n🎉 Coverage analysis complete!")
    print("📁 Check the following files:")
    print("   - htmlcov/index.html (Interactive HTML report)")
    print("   - coverage.xml (XML report for CI/CD)")
    print("   - coverage_report.md (Detailed markdown report)")

if __name__ == '__main__':
    main() 