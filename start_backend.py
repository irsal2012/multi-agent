"""
Startup script for the FastAPI backend server.
"""

import os
import sys
import subprocess
import logging

def main():
    """Start the FastAPI backend server."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    if not os.path.exists(backend_dir):
        logger.error("Backend directory not found!")
        sys.exit(1)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Add backend directory to Python path
    sys.path.insert(0, backend_dir)
    
    logger.info("Starting FastAPI backend server...")
    logger.info("Backend will be available at: http://localhost:8000")
    logger.info("API documentation will be available at: http://localhost:8000/docs")
    
    try:
        # Start the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("Backend server stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start backend server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
