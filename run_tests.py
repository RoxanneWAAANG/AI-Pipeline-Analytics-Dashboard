#!/usr/bin/env python3
"""
Simple Test Runner for AI Pipeline Analytics Dashboard
Runs tests and generates basic coverage report
"""

import subprocess
import sys
import os

def run_basic_tests():
    """Run basic test suite with coverage"""
    print("🧪 Running AI Pipeline Analytics Tests")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('analytics_dashboard.py'):
        print("❌ Error: analytics_dashboard.py not found")
        print("Please run this script from the project root directory")
        return False
    
    # Simple test run
    try:
        print("📊 Running tests with coverage...")
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/', '-v',
            '--cov=analytics_dashboard',
            '--cov-report=term-missing',
            '--cov-report=html',
            '--tb=short'
        ], check=True)
        
        print("\n✅ Tests completed successfully!")
        print("📄 Coverage report available in htmlcov/index.html")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-cov")
        return False

def run_quick_demo():
    """Run a quick demo of the dashboard"""
    print("\n🚀 Starting Quick Demo...")
    
    try:
        # Import and test basic functionality
        import analytics_dashboard
        
        # Create analytics instance
        analytics = analytics_dashboard.AIPipelineAnalytics()
        print("✅ Analytics instance created")
        
        # Generate some mock data
        df = analytics.generate_mock_data(hours=1)
        print(f"✅ Generated {len(df)} mock records")
        
        # Calculate metrics
        metrics = analytics.calculate_performance_metrics(df)
        print(f"✅ Calculated metrics:")
        print(f"   - Total executions: {metrics.get('total_executions', 0)}")
        print(f"   - Success rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"   - Avg response time: {metrics.get('avg_response_time', 0):.0f}ms")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🎯 AI Pipeline Analytics - Quick Test & Demo")
    print("=" * 50)
    
    # Run tests
    test_success = run_basic_tests()
    
    # Run demo
    demo_success = run_quick_demo()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"   Tests: {'✅ PASSED' if test_success else '❌ FAILED'}")
    print(f"   Demo:  {'✅ PASSED' if demo_success else '❌ FAILED'}")
    
    if test_success and demo_success:
        print("\n🎉 All systems working! Ready for final project submission.")
        print("\n🚀 Quick Start Commands:")
        print("   python run_demo_dashboard.py   # Launch dashboard")
        print("   python run_tests.py            # Run this test suite")
        
        return True
    else:
        print("\n⚠️ Some issues detected. Check the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 