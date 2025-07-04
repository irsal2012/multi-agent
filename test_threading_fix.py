#!/usr/bin/env python3
"""
Test script to verify the threading fix for UI generation.
"""

import requests
import json
import time
import sys

def test_pipeline_execution():
    """Test that the pipeline completes without threading errors."""
    
    print("🧪 Testing Threading Fix for UI Generation")
    print("=" * 50)
    
    # Test data
    test_request = {
        "user_input": "Create a simple calculator with add, subtract, multiply, and divide functions",
        "project_name": "threading_fix_test"
    }
    
    try:
        # Step 1: Start pipeline
        print("📤 Starting pipeline execution...")
        response = requests.post(
            "http://localhost:8000/api/v1/pipeline/generate",
            json=test_request,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start pipeline: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        project_id = result.get("project_id")
        
        if not project_id:
            print("❌ No project ID returned")
            return False
        
        print(f"✅ Pipeline started successfully")
        print(f"📋 Project ID: {project_id}")
        print(f"🔗 Progress URL: {result.get('progress_url', 'N/A')}")
        
        # Step 2: Monitor progress
        print("\n📊 Monitoring pipeline progress...")
        max_wait_time = 300  # 5 minutes max
        start_time = time.time()
        last_progress = -1
        ui_generation_started = False
        ui_generation_completed = False
        
        while time.time() - start_time < max_wait_time:
            try:
                progress_response = requests.get(
                    f"http://localhost:8000/api/v1/progress/{project_id}",
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    current_progress = progress_data.get("progress_percentage", 0)
                    is_completed = progress_data.get("is_completed", False)
                    has_failures = progress_data.get("has_failures", False)
                    current_step = progress_data.get("current_step_info", {})
                    
                    # Check for UI generation step
                    if current_step and "UI" in current_step.get("name", ""):
                        if not ui_generation_started:
                            print("🎨 UI Generation step started - testing threading fix...")
                            ui_generation_started = True
                        
                        if current_step.get("status") == "completed":
                            if not ui_generation_completed:
                                print("✅ UI Generation completed successfully!")
                                ui_generation_completed = True
                    
                    # Print progress updates
                    if current_progress != last_progress:
                        step_name = current_step.get("name", "Unknown") if current_step else "Unknown"
                        print(f"📈 Progress: {current_progress:.1f}% - {step_name}")
                        last_progress = current_progress
                    
                    # Check completion
                    if is_completed:
                        if has_failures:
                            print("⚠️  Pipeline completed with failures")
                            return False
                        else:
                            print("🎉 Pipeline completed successfully!")
                            return True
                    
                    # Check for failures
                    if has_failures:
                        print("❌ Pipeline failed during execution")
                        steps = progress_data.get("steps", [])
                        for step in steps:
                            if step.get("status") == "failed":
                                print(f"   Failed step: {step.get('name', 'Unknown')}")
                        return False
                
                time.sleep(2)  # Check every 2 seconds
                
            except requests.RequestException as e:
                print(f"⚠️  Error checking progress: {e}")
                time.sleep(5)  # Wait longer on error
        
        print("⏰ Pipeline execution timed out")
        return False
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_backend_status():
    """Check if the backend is running."""
    try:
        response = requests.get("http://localhost:8000/api/v1/agents/info", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test function."""
    print("🔍 Checking backend status...")
    
    if not check_backend_status():
        print("❌ Backend is not running. Please start it with: python start_backend.py")
        sys.exit(1)
    
    print("✅ Backend is running")
    
    # Run the test
    success = test_pipeline_execution()
    
    if success:
        print("\n🎉 THREADING FIX TEST PASSED!")
        print("✅ UI Generation completed without threading errors")
        print("✅ Pipeline executed successfully end-to-end")
    else:
        print("\n❌ THREADING FIX TEST FAILED!")
        print("❌ Check the logs for threading or other errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
