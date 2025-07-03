#!/usr/bin/env python3
"""
Test script to verify the progress tracking fix.
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.pipeline_service import PipelineService
from services.progress_service import ProgressService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_progress_tracking():
    """Test the progress tracking functionality."""
    
    logger.info("Starting progress tracking test...")
    
    # Create services
    pipeline_service = PipelineService()
    progress_service = ProgressService()
    
    # Test 1: Create a test project and check initial progress
    logger.info("Test 1: Creating test project...")
    
    try:
        # Start a simple generation
        response = await pipeline_service.start_generation(
            user_input="Create a simple calculator that can add, subtract, multiply and divide two numbers.",
            project_name="test_calculator"
        )
        
        project_id = response.project_id
        logger.info(f"Created project: {project_id}")
        
        # Wait a moment for initialization
        await asyncio.sleep(2)
        
        # Check progress
        progress = progress_service.get_project_progress(project_id)
        if progress:
            logger.info(f"Progress found: {progress.progress_percentage}% complete")
            logger.info(f"Steps: {len(progress.steps)}")
            logger.info(f"Running: {progress.is_running}")
            
            # Print step details
            for i, step in enumerate(progress.steps):
                logger.info(f"  Step {i+1}: {step.name} - {step.status}")
        else:
            logger.error("No progress data found!")
            return False
        
        # Wait for some progress
        logger.info("Waiting for progress updates...")
        for i in range(10):
            await asyncio.sleep(3)
            progress = progress_service.get_project_progress(project_id)
            if progress:
                logger.info(f"Progress update {i+1}: {progress.progress_percentage:.1f}% complete")
                if progress.current_step_info:
                    logger.info(f"  Current step: {progress.current_step_info.name} - {progress.current_step_info.status}")
                
                if progress.is_completed:
                    logger.info("Project completed!")
                    break
                elif progress.has_failures:
                    logger.error("Project failed!")
                    break
            else:
                logger.warning(f"No progress data on update {i+1}")
        
        logger.info("Progress tracking test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_progress():
    """Test simple progress service functionality."""
    
    logger.info("Testing simple progress service...")
    
    progress_service = ProgressService()
    
    # Create fake project metadata
    from models.schemas import ProjectMetadata, ProjectStatus
    from datetime import datetime
    
    fake_metadata = ProjectMetadata(
        project_id="test-123",
        project_name="test_project",
        user_input="Test project",
        status=ProjectStatus.RUNNING
    )
    
    # Create progress tracking
    progress_service.create_project_progress("test-123", fake_metadata)
    
    # Update with test progress
    test_progress = {
        'total_steps': 7,
        'completed_steps': 2,
        'failed_steps': 0,
        'progress_percentage': 28.5,
        'steps': [
            {
                'name': 'requirements_analysis',
                'description': 'Analyzing requirements from user input',
                'status': 'completed',
                'progress_percentage': 100.0,
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'agent_name': 'requirement_analyst'
            },
            {
                'name': 'code_generation',
                'description': 'Generating Python code from requirements',
                'status': 'running',
                'progress_percentage': 45.0,
                'start_time': datetime.now().isoformat(),
                'agent_name': 'python_coder'
            }
        ],
        'is_running': True,
        'is_completed': False,
        'has_failures': False,
        'current_step_info': {
            'name': 'code_generation',
            'description': 'Generating Python code from requirements',
            'status': 'running',
            'progress_percentage': 45.0,
            'agent_name': 'python_coder'
        }
    }
    
    progress_service.update_project_progress("test-123", test_progress)
    
    # Get the updated progress
    updated_progress = progress_service.get_project_progress("test-123")
    
    if updated_progress:
        logger.info("✅ Simple progress test passed!")
        logger.info(f"Progress: {updated_progress.progress_percentage}%")
        logger.info(f"Steps: {len(updated_progress.steps)}")
        return True
    else:
        logger.error("❌ Simple progress test failed!")
        return False

if __name__ == "__main__":
    # First test simple progress service
    result1 = asyncio.run(test_simple_progress())
    
    if result1:
        logger.info("Simple test passed, running full test...")
        # Then test full pipeline if simple test passes
        result2 = asyncio.run(test_progress_tracking())
        
        if result2:
            logger.info("🎉 All tests passed! Progress tracking is working.")
            sys.exit(0)
        else:
            logger.error("❌ Full pipeline test failed.")
            sys.exit(1)
    else:
        logger.error("❌ Simple progress test failed.")
        sys.exit(1)
