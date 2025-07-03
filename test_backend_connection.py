#!/usr/bin/env python3
"""
Test script to verify backend connection and health check functionality.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

def test_basic_connection(base_url: str = "http://localhost:8000") -> bool:
    """Test basic HTTP connection to backend."""
    print("🔗 Testing basic HTTP connection...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Basic HTTP connection successful")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ HTTP connection failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic HTTP connection failed: {str(e)}")
        return False

def test_health_check(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Test the enhanced health check endpoint."""
    print("\n🏥 Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check endpoint accessible")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Ready: {health_data.get('ready', 'unknown')}")
            
            # Show service status
            services = health_data.get('services', {})
            if services:
                print("   Service Status:")
                for service_name, service_status in services.items():
                    status_icon = "✅" if "healthy" in str(service_status) else "❌"
                    print(f"     {status_icon} {service_name}: {service_status}")
            
            return health_data
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return {"status": "error", "ready": False}
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return {"status": "unreachable", "ready": False}

def test_api_endpoints(base_url: str = "http://localhost:8000") -> bool:
    """Test key API endpoints."""
    print("\n🔌 Testing API endpoints...")
    
    endpoints_to_test = [
        ("/api/v1/pipeline/status", "Pipeline status"),
        ("/api/v1/agents/info", "Agent information"),
        ("/api/v1/projects/statistics", "Project statistics"),
    ]
    
    all_passed = True
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {description}: OK")
            else:
                print(f"   ❌ {description}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {description}: {str(e)}")
            all_passed = False
    
    return all_passed

def test_input_validation(base_url: str = "http://localhost:8000") -> bool:
    """Test input validation endpoint."""
    print("\n✅ Testing input validation...")
    try:
        payload = {"user_input": "Create a simple calculator application"}
        response = requests.post(
            f"{base_url}/api/v1/pipeline/validate", 
            json=payload, 
            timeout=5
        )
        if response.status_code == 200:
            validation_result = response.json()
            print("   ✅ Input validation: OK")
            print(f"   Valid: {validation_result.get('is_valid', 'unknown')}")
            return True
        else:
            print(f"   ❌ Input validation failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Input validation failed: {str(e)}")
        return False

def wait_for_backend(base_url: str = "http://localhost:8000", max_wait: int = 30) -> bool:
    """Wait for backend to become available."""
    print(f"⏳ Waiting for backend at {base_url} (max {max_wait}s)...")
    
    for attempt in range(max_wait):
        try:
            response = requests.get(base_url, timeout=2)
            if response.status_code == 200:
                print(f"✅ Backend is available after {attempt + 1}s")
                return True
        except:
            pass
        
        if attempt < max_wait - 1:
            print(f"   Attempt {attempt + 1}/{max_wait}...")
            time.sleep(1)
    
    print(f"❌ Backend not available after {max_wait}s")
    return False

def main():
    """Main test function."""
    print("🧪 Backend Connection Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Wait for backend
    if not wait_for_backend(base_url):
        print("\n❌ Backend is not running. Please start it with:")
        print("   python start_backend.py")
        sys.exit(1)
    
    # Test 2: Basic connection
    if not test_basic_connection(base_url):
        print("\n❌ Basic connection test failed")
        sys.exit(1)
    
    # Test 3: Health check
    health_data = test_health_check(base_url)
    if not health_data.get('ready', False):
        print("\n⚠️  Backend is running but not ready")
        print("   This may indicate service initialization issues")
        
        # Show detailed health info
        print("\n🔍 Detailed Health Information:")
        print(json.dumps(health_data, indent=2, default=str))
        
        # Continue with other tests anyway
    
    # Test 4: API endpoints
    api_success = test_api_endpoints(base_url)
    
    # Test 5: Input validation
    validation_success = test_input_validation(base_url)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Basic Connection: ✅")
    print(f"   Health Check: {'✅' if health_data.get('ready') else '⚠️'}")
    print(f"   API Endpoints: {'✅' if api_success else '❌'}")
    print(f"   Input Validation: {'✅' if validation_success else '❌'}")
    
    if health_data.get('ready') and api_success and validation_success:
        print("\n🎉 All tests passed! Backend is ready for frontend connection.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
