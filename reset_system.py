#!/usr/bin/env python3
"""
Reset script to clear any stale state and restart the system cleanly.
"""

import requests
import time
import sys
import subprocess
import os
import signal

def check_process_running(port):
    """Check if a process is running on the given port."""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return True
    except:
        return False

def kill_processes_on_port(port):
    """Kill processes running on the specified port."""
    try:
        # Find processes using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"Terminated process {pid} on port {port}")
                    time.sleep(1)
                    # Force kill if still running
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Process already terminated
                except (ValueError, ProcessLookupError):
                    pass
    except Exception as e:
        print(f"Error killing processes on port {port}: {e}")

def reset_system():
    """Reset the entire system to a clean state."""
    
    print("🔄 Resetting Multi-Agent Code Generator System...")
    
    # Step 1: Stop existing processes
    print("\n1. Stopping existing processes...")
    
    # Kill backend (port 8000)
    if check_process_running(8000):
        print("   Stopping backend on port 8000...")
        kill_processes_on_port(8000)
        time.sleep(2)
    
    # Kill frontend (port 8501)
    if check_process_running(8501):
        print("   Stopping frontend on port 8501...")
        kill_processes_on_port(8501)
        time.sleep(2)
    
    # Step 2: Clear any temporary files or caches
    print("\n2. Clearing temporary files...")
    
    # Clear Python cache
    subprocess.run(['find', '.', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'], 
                   capture_output=True)
    subprocess.run(['find', '.', '-name', '*.pyc', '-delete'], capture_output=True)
    
    # Clear Streamlit cache directory if it exists
    streamlit_cache_dir = os.path.expanduser("~/.streamlit")
    if os.path.exists(streamlit_cache_dir):
        try:
            subprocess.run(['rm', '-rf', streamlit_cache_dir], capture_output=True)
            print("   Cleared Streamlit cache")
        except:
            pass
    
    print("\n3. Verifying processes are stopped...")
    time.sleep(2)
    
    backend_running = check_process_running(8000)
    frontend_running = check_process_running(8501)
    
    if backend_running:
        print("   ⚠️  Backend still running on port 8000")
    else:
        print("   ✅ Backend stopped")
    
    if frontend_running:
        print("   ⚠️  Frontend still running on port 8501")
    else:
        print("   ✅ Frontend stopped")
    
    print("\n4. Starting fresh instances...")
    
    # Start backend
    print("   Starting backend...")
    backend_process = subprocess.Popen(
        ['python', 'start_backend.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    print("   Waiting for backend to initialize...")
    for i in range(30):  # Wait up to 30 seconds
        if check_process_running(8000):
            print("   ✅ Backend started successfully")
            break
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    else:
        print("   ❌ Backend failed to start within 30 seconds")
        return False
    
    # Test backend health
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend health check passed")
        else:
            print(f"   ⚠️  Backend health check returned status {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Backend health check failed: {e}")
    
    # Start frontend
    print("   Starting frontend...")
    frontend_process = subprocess.Popen(
        ['python', 'start_frontend.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for frontend to start
    print("   Waiting for frontend to initialize...")
    for i in range(30):  # Wait up to 30 seconds
        if check_process_running(8501):
            print("   ✅ Frontend started successfully")
            break
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    else:
        print("   ❌ Frontend failed to start within 30 seconds")
        return False
    
    print("\n🎉 System reset complete!")
    print("\n📋 Next steps:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. The system should now be in a clean state")
    print("   3. You can start a new code generation project")
    print("\n💡 If you see any stale progress data in the UI:")
    print("   - Click the '🔄 Clear Cache' button in the sidebar")
    print("   - Refresh the browser page")
    
    return True

if __name__ == "__main__":
    try:
        success = reset_system()
        if success:
            print("\n✅ Reset completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Reset encountered issues")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Reset interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Reset failed with error: {e}")
        sys.exit(1)
