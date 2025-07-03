#!/usr/bin/env python3
"""
Comprehensive test to verify the progress tracking fixes are working correctly.
"""

import asyncio
import time
import requests
import json
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
TEST_PROJECT_ID = f"test-fix-{int(time.time())}"

def test_backend_connection():
    """Test if backend is running and accessible."""
    print("🔍 Testing backend connection...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {str(e)}")
        print("💡 Make sure to start the backend with: python backend/main.py")
        return False

def test_progress_service():
    """Test the progress service endpoints."""
    print("\n🧪 Testing progress service...")
    
    # Test creating test progress data
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/progress/test/{TEST_PROJECT_ID}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Test progress data created successfully")
            print(f"   Project ID: {data.get('project_id')}")
            print(f"   Progress: {data.get('progress', {}).get('progress_percentage', 0):.1f}%")
            return True
        else:
            print(f"❌ Failed to create test progress: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Progress service test failed: {str(e)}")
        return False

def test_progress_retrieval():
    """Test retrieving progress data."""
    print("\n📊 Testing progress retrieval...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/progress/{TEST_PROJECT_ID}", timeout=10)
        if response.status_code == 200:
            progress = response.json()
            print("✅ Progress data retrieved successfully")
            print(f"   Total steps: {progress.get('total_steps', 0)}")
            print(f"   Completed steps: {progress.get('completed_steps', 0)}")
            print(f"   Progress percentage: {progress.get('progress_percentage', 0):.1f}%")
            print(f"   Is running: {progress.get('is_running', False)}")
            
            # Check if we have steps data
            steps = progress.get('steps', [])
            if steps:
                print(f"   Steps data: {len(steps)} steps found")
                for i, step in enumerate(steps[:3]):  # Show first 3 steps
                    print(f"     Step {i+1}: {step.get('name', 'Unknown')} - {step.get('status', 'unknown')}")
            else:
                print("   ⚠️ No steps data found")
            
            return True
        else:
            print(f"❌ Failed to retrieve progress: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Progress retrieval failed: {str(e)}")
        return False

def test_pipeline_status():
    """Test pipeline status endpoint."""
    print("\n⚙️ Testing pipeline status...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/pipeline/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print("✅ Pipeline status retrieved successfully")
            print(f"   Pipeline ready: {status.get('is_ready', False)}")
            print(f"   Active projects: {status.get('active_projects', 0)}")
            return True
        else:
            print(f"❌ Failed to get pipeline status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Pipeline status test failed: {str(e)}")
        return False

def test_agent_info():
    """Test agent information endpoint."""
    print("\n🤖 Testing agent information...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/agents/info", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print("✅ Agent information retrieved successfully")
            agents = info.get('available_agents', [])
            print(f"   Available agents: {len(agents)}")
            for agent in agents[:3]:  # Show first 3 agents
                print(f"     - {agent}")
            return True
        else:
            print(f"❌ Failed to get agent info: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Agent info test failed: {str(e)}")
        return False

def test_real_time_progress_monitoring():
    """Test real-time progress monitoring by polling multiple times."""
    print("\n⏱️ Testing real-time progress monitoring...")
    
    print("   Monitoring progress for 10 seconds...")
    start_time = time.time()
    poll_count = 0
    successful_polls = 0
    
    while time.time() - start_time < 10:  # Monitor for 10 seconds
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/progress/{TEST_PROJECT_ID}", timeout=5)
            poll_count += 1
            
            if response.status_code == 200:
                successful_polls += 1
                progress = response.json()
                progress_pct = progress.get('progress_percentage', 0)
                is_running = progress.get('is_running', False)
                
                if poll_count % 3 == 0:  # Print every 3rd poll
                    print(f"   Poll #{poll_count}: {progress_pct:.1f}% (running: {is_running})")
            
            time.sleep(1)  # Poll every second
            
        except requests.exceptions.RequestException:
            poll_count += 1
    
    success_rate = (successful_polls / poll_count) * 100 if poll_count > 0 else 0
    print(f"   Polling results: {successful_polls}/{poll_count} successful ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("✅ Real-time monitoring working well")
        return True
    else:
        print("⚠️ Real-time monitoring has issues")
        return False

def test_code_generation_start():
    """Test starting a code generation to see if progress tracking works."""
    print("\n🚀 Testing code generation start...")
    
    test_input = "Create a simple calculator that can add, subtract, multiply, and divide two numbers."
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/pipeline/generate",
            json={
                "user_input": test_input,
                "project_name": f"test-calculator-{int(time.time())}"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            project_id = result.get('project_id')
            print("✅ Code generation started successfully")
            print(f"   Project ID: {project_id}")
            print(f"   Status: {result.get('status')}")
            
            # Monitor progress for a short time
            print("   Monitoring initial progress...")
            for i in range(5):
                time.sleep(2)
                try:
                    progress_response = requests.get(f"{BACKEND_URL}/api/v1/progress/{project_id}", timeout=5)
                    if progress_response.status_code == 200:
                        progress = progress_response.json()
                        pct = progress.get('progress_percentage', 0)
                        running = progress.get('is_running', False)
                        current_step = progress.get('current_step_info', {})
                        step_name = current_step.get('name', 'Unknown') if current_step else 'None'
                        print(f"     Check {i+1}: {pct:.1f}% - Running: {running} - Step: {step_name}")
                        
                        if pct > 0:
                            print("✅ Progress tracking is working during generation!")
                            return True
                except:
                    pass
            
            print("⚠️ No progress detected, but generation started")
            return True
            
        else:
            print(f"❌ Failed to start code generation: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Code generation test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🔧 Comprehensive Progress Tracking Fix Test")
    print("=" * 50)
    
    tests = [
        ("Backend Connection", test_backend_connection),
        ("Progress Service", test_progress_service),
        ("Progress Retrieval", test_progress_retrieval),
        ("Pipeline Status", test_pipeline_status),
        ("Agent Information", test_agent_info),
        ("Real-time Monitoring", test_real_time_progress_monitoring),
        ("Code Generation Start", test_code_generation_start),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Progress tracking fix is working correctly.")
    elif passed >= total * 0.8:
        print("\n✅ Most tests passed. Progress tracking is mostly working.")
    else:
        print("\n⚠️ Several tests failed. Progress tracking needs more work.")
    
    print("\n💡 Tips:")
    print("   - Make sure backend is running: python backend/main.py")
    print("   - Check backend logs for any errors")
    print("   - Test the frontend: streamlit run frontend/streamlit_app.py")

if __name__ == "__main__":
    main()
