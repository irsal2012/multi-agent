#!/usr/bin/env python3
"""
Test script to verify smart completion detection functionality.
"""

import sys
import os
sys.path.append('frontend')

from client.api_client import APIClient

def test_smart_completion():
    """Test the smart completion detection with existing project."""
    
    # Initialize API client
    api_client = APIClient()
    
    # Test with the existing completed project ID
    project_id = "ab8fd6c6-e2b9-4696-8759-221ee4143ef9"  # From testing project
    
    print(f"Testing smart completion detection for project: {project_id}")
    print("=" * 60)
    
    # Test 1: Try to get progress (should fail since progress service has no memory)
    print("1. Testing progress API (should fail)...")
    progress = api_client.get_project_progress(project_id)
    if progress:
        print("   ✅ Progress found:", progress.get('progress_percentage', 0), "%")
    else:
        print("   ❌ Progress not found (expected)")
    
    print()
    
    # Test 2: Try smart completion detection fallback
    print("2. Testing smart completion detection fallback...")
    completion_status = api_client.check_project_completion_fallback(project_id)
    
    if completion_status:
        print("   ✅ Smart completion detection result:")
        print(f"      - Is completed: {completion_status.get('is_completed')}")
        print(f"      - Has result: {completion_status.get('has_result')}")
        
        if completion_status.get('result'):
            result = completion_status['result']
            print(f"      - Project name: {result.get('project_name', 'Unknown')}")
            print(f"      - Has code: {'code' in result}")
            print(f"      - Has documentation: {'documentation' in result}")
            print(f"      - Has tests: {'tests' in result}")
            print(f"      - Has UI: {'ui' in result}")
        else:
            print("      - No result data found")
    else:
        print("   ❌ Smart completion detection failed")
    
    print()
    
    # Test 3: Direct result API call
    print("3. Testing direct result API call...")
    result = api_client.get_project_result(project_id)
    if result:
        print("   ✅ Direct result found:")
        print(f"      - Project name: {result.get('project_name', 'Unknown')}")
        print(f"      - Has code: {'code' in result}")
        print(f"      - Has documentation: {'documentation' in result}")
    else:
        print("   ❌ Direct result not found")
    
    print()
    print("=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_smart_completion()
