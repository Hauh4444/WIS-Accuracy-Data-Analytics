#!/usr/bin/env python3
"""
Script to run safe tests that don't require database or GUI environments.
This script runs the core tests that work in any environment.
"""

import subprocess
import sys
import os

def run_safe_tests():
    """Run tests that are safe to run in any environment."""
    
    # Safe test files that don't require database or GUI
    safe_tests = [
        "tests/test_models.py",
        "tests/test_paths.py"
    ]
    
    print("Running safe tests (no database or GUI required)...")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the tests
    cmd = [sys.executable, "-m", "pytest"] + safe_tests + ["-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ All safe tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    success = run_safe_tests()
    sys.exit(0 if success else 1)
