"""
Main pipeline orchestrator for the Multi-Agent Framework.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.agent_manager import AgentManager
from core.utils import setup_logging, save_json

class MultiAgentPipeline:
    """Main pipeline class that orchestrates the multi-agent workflow."""
    
    def __init__(self, output_dir: str = "output"):
        self.logger = setup_logging()
        self.agent_manager = AgentManager(output_dir)
        self.pipeline_history = []
        
    def run_pipeline(self, user_input: str, project_name: str = None) -> Dict[str, Any]:
        """
        Run the complete multi-agent pipeline.
        
        Args:
            user_input: Natural language description of the software to build
            project_name: Optional project name (auto-generated if not provided)
            
        Returns:
            Dictionary containing all pipeline results
        """
        start_time = datetime.now()
        self.logger.info(f"Starting multi-agent pipeline at {start_time}")
        
        try:
            # Reset progress for new pipeline run
            self.agent_manager.reset_progress()
            
            # Process through all agents
            results = self.agent_manager.process_user_input(user_input, project_name)
            
            # Calculate total execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Add pipeline metadata
            results['pipeline_metadata'] = {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'execution_time_seconds': execution_time,
                'success': True
            }
            
            # Store in history
            self.pipeline_history.append({
                'timestamp': start_time.isoformat(),
                'project_name': results['project_name'],
                'user_input': user_input,
                'success': True,
                'execution_time': execution_time
            })
            
            self.logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            return results
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_result = {
                'error': str(e),
                'pipeline_metadata': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'execution_time_seconds': execution_time,
                    'success': False
                },
                'progress': self.agent_manager.get_progress()
            }
            
            # Store failed run in history
            self.pipeline_history.append({
                'timestamp': start_time.isoformat(),
                'project_name': project_name or 'unknown',
                'user_input': user_input,
                'success': False,
                'execution_time': execution_time,
                'error': str(e)
            })
            
            self.logger.error(f"Pipeline failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and progress."""
        try:
            current_progress = self.agent_manager.get_progress()
        except Exception as e:
            # Fallback if agent manager progress is not available
            current_progress = {
                'total_steps': 0,
                'completed_steps': 0,
                'failed_steps': 0,
                'progress_percentage': 0,
                'steps': [],
                'elapsed_time': 0,
                'estimated_remaining_time': 0,
                'is_running': False,
                'is_completed': False,
                'has_failures': False,
                'logs': []
            }
        
        return {
            'current_progress': current_progress,
            'pipeline_history': self.pipeline_history,
            'total_runs': len(self.pipeline_history),
            'successful_runs': sum(1 for run in self.pipeline_history if run['success']),
            'failed_runs': sum(1 for run in self.pipeline_history if not run['success'])
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all available agents."""
        return {
            'available_agents': list(self.agent_manager.agents.keys()),
            'agent_descriptions': {
                'requirement_analyst': 'Analyzes natural language input and creates structured requirements',
                'python_coder': 'Generates high-quality Python code from requirements',
                'code_reviewer': 'Reviews code for quality, security, and best practices',
                'documentation_writer': 'Creates comprehensive documentation',
                'test_generator': 'Generates comprehensive test suites',
                'deployment_engineer': 'Creates deployment configurations and scripts',
                'ui_designer': 'Creates Streamlit user interfaces'
            },
            'pipeline_steps': [
                'Requirements Analysis',
                'Code Generation', 
                'Code Review & Iteration',
                'Documentation Generation',
                'Test Case Generation',
                'Deployment Configuration',
                'UI Generation'
            ]
        }
    
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        Validate user input before running pipeline.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Validation result with suggestions
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'suggestions': []
        }
        
        # Check input length
        if len(user_input.strip()) < 10:
            validation_result['warnings'].append(
                "Input is very short. Consider providing more detailed requirements."
            )
        
        if len(user_input.strip()) > 5000:
            validation_result['warnings'].append(
                "Input is very long. Consider breaking it into smaller, focused requirements."
            )
        
        # Check for common keywords that indicate good requirements
        good_keywords = [
            'function', 'feature', 'user', 'system', 'data', 'interface',
            'requirement', 'should', 'must', 'will', 'can', 'allow'
        ]
        
        found_keywords = sum(1 for keyword in good_keywords if keyword.lower() in user_input.lower())
        
        if found_keywords < 2:
            validation_result['suggestions'].append(
                "Consider including more specific functional requirements (what the system should do)."
            )
        
        # Check for technical context
        tech_keywords = [
            'python', 'web', 'api', 'database', 'file', 'process',
            'algorithm', 'data', 'input', 'output'
        ]
        
        found_tech = sum(1 for keyword in tech_keywords if keyword.lower() in user_input.lower())
        
        if found_tech == 0:
            validation_result['suggestions'].append(
                "Consider specifying the technical domain or type of application you want to build."
            )
        
        return validation_result

# Global pipeline instance
pipeline = MultiAgentPipeline()
