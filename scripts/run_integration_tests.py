#!/usr/bin/env python3
"""
Integration test runner for Todo API.
"""

import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path

def get_api_url():
    """Get API URL from CDK outputs or environment."""
    # Try environment variable first
    api_url = os.environ.get('API_BASE_URL')
    if api_url:
        return api_url.rstrip('/')
    
    # Try CDK outputs file
    outputs_files = [
        'cdk-outputs-test.json',
        'cdk-outputs.json'
    ]
    
    for file_name in outputs_files:
        if Path(file_name).exists():
            try:
                with open(file_name, 'r') as f:
                    outputs = json.load(f)
                
                # Look for TodoApiUrl in any stack
                for stack_name, stack_outputs in outputs.items():
                    if 'TodoApiUrl' in stack_outputs:
                        return stack_outputs['TodoApiUrl'].rstrip('/')
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
    
    return None

def main():
    """Run integration tests."""
    print("🚀 Starting integration tests...")
    
    # Get API URL
    api_url = get_api_url()
    if not api_url:
        print("❌ Could not find API URL")
        print("Make sure cdk-outputs-test.json exists or set API_BASE_URL environment variable")
        sys.exit(1)
    
    print(f"🔗 Using API URL: {api_url}")
    
    # Set environment variable for tests
    os.environ['API_BASE_URL'] = api_url
    
    # Run tests
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'src/tests/integration_test.py',
            '-v', '--tb=short'
        ], check=True)
        
        print("✅ All integration tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Integration tests failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)