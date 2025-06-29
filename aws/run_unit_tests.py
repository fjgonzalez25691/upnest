"""
Test runner script for unit tests.
Runs all unit tests for shared utilities with coverage reporting.
"""

import subprocess
import sys
import os

def run_tests():
    """Run unit tests for shared utilities."""
    print("🧪 Running Unit Tests for Shared Utilities...")
    print("=" * 60)
    
    # Change to aws directory
    aws_dir = os.path.dirname(__file__)
    os.chdir(aws_dir)
    
    # Test files to run
    test_files = [
        'tests/test_jwt_validation.py',
        'tests/test_dynamodb_client.py',
        'tests/test_validation_utils.py'
    ]
    
    all_passed = True
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', test_file, '-v'
            ], capture_output=True, text=True, check=False)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode != 0:
                all_passed = False
                print(f"❌ {test_file} FAILED")
            else:
                print(f"✅ {test_file} PASSED")
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL UNIT TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

def run_with_coverage():
    """Run tests with coverage reporting."""
    print("🧪 Running Unit Tests with Coverage...")
    print("=" * 60)
    
    try:
        # Install pytest and coverage if not available
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'coverage'], check=False)
        
        # Run tests with coverage
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/', '--cov=lambdas/shared', '--cov-report=term-missing'
        ], check=False)
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests with coverage: {e}")
        return 1

if __name__ == '__main__':
    # Check if coverage flag is provided
    if '--coverage' in sys.argv:
        exit_code = run_with_coverage()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
