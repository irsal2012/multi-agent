"""
Startup script for the Streamlit frontend.
"""

import os
import sys
import subprocess
import logging

def main():
    """Start the Streamlit frontend."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    if not os.path.exists(frontend_dir):
        logger.error("Frontend directory not found!")
        sys.exit(1)
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Add frontend directory to Python path
    sys.path.insert(0, frontend_dir)
    
    logger.info("Starting Streamlit frontend...")
    logger.info("Frontend will be available at: http://localhost:8501")
    logger.info("Make sure the backend is running at: http://localhost:8000")
    
    try:
        # Start the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--server.headless", "false"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("Frontend server stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start frontend server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
