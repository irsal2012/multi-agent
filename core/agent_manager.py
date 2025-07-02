"""
Agent Manager for coordinating multiple AutoGen agents.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

import autogen
from config.model_config import model_config
from agents import (
    RequirementAnalyst, PythonCoder, CodeReviewer, DocumentationWriter,
    TestGenerator, DeploymentEngineer, UIDesigner
)
from core.utils import (
    setup_logging, save_json, save_text, generate_timestamp,
    validate_requirements, extract_code_blocks, ProgressTracker
)

class AgentManager:
    """Manages and coordinates all agents in the multi-agent framework."""
    
    def __init__(self, output_dir: str = "output"):
        self.logger = setup_logging()
        self.output_dir = output_dir
        self.progress_tracker = ProgressTracker()
        self.agents = {}
        self.conversation_history = []
        self.current_project = None
        
        # Initialize progress tracking steps
        self._setup_progress_steps()
        
        # Initialize agents
        self._initialize_agents()
    
    def _setup_progress_steps(self):
        """Set up progress tracking steps with estimated durations."""
        steps = [
            ("requirements_analysis", "Analyzing requirements from user input", 25.0),
            ("code_generation", "Generating Python code from requirements", 45.0),
            ("code_review", "Reviewing code for quality and security", 30.0),
            ("documentation", "Creating comprehensive documentation", 20.0),
            ("test_generation", "Generating test cases", 25.0),
            ("deployment_config", "Creating deployment configurations", 15.0),
            ("ui_generation", "Creating Streamlit user interface", 20.0)
        ]
        
        for step_name, description, estimated_duration in steps:
            self.progress_tracker.add_step(step_name, description, estimated_duration)
    
    def _initialize_agents(self):
        """Initialize all AutoGen agents."""
        try:
            # Requirement Analysis Agent
            self.agents['requirement_analyst'] = RequirementAnalyst.create_agent(
                model_config.get_llm_config()
            )
            
            # Coding Agent
            self.agents['python_coder'] = PythonCoder.create_agent(
                model_config.get_coding_config()
            )
            
            # Code Review Agent
            self.agents['code_reviewer'] = CodeReviewer.create_agent(
                model_config.get_review_config()
            )
            
            # Documentation Agent
            self.agents['documentation_writer'] = DocumentationWriter.create_agent(
                model_config.get_creative_config()
            )
            
            # Test Generation Agent
            self.agents['test_generator'] = TestGenerator.create_agent(
                model_config.get_coding_config()
            )
            
            # Deployment Agent
            self.agents['deployment_engineer'] = DeploymentEngineer.create_agent(
                model_config.get_llm_config()
            )
            
            # UI Agent
            self.agents['ui_designer'] = UIDesigner.create_agent(
                model_config.get_creative_config()
            )
            
            # User Proxy Agent for coordination
            self.agents['user_proxy'] = autogen.UserProxyAgent(
                name="UserProxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
                code_execution_config=False,
            )
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    def process_user_input(self, user_input: str, project_name: str = None) -> Dict[str, Any]:
        """Process user input through the complete agent pipeline."""
        if not project_name:
            project_name = f"project_{generate_timestamp()}"
        
        self.current_project = project_name
        self.logger.info(f"Starting pipeline for project: {project_name}")
        
        try:
            # Step 1: Requirements Analysis
            requirements = self._analyze_requirements(user_input)
            
            # Step 2: Code Generation
            code_result = self._generate_code(requirements)
            
            # Step 3: Code Review and Iteration
            reviewed_code = self._review_code(code_result, requirements)
            
            # Step 4: Documentation Generation
            documentation = self._generate_documentation(reviewed_code, requirements)
            
            # Step 5: Test Case Generation
            tests = self._generate_tests(reviewed_code, requirements)
            
            # Step 6: Deployment Configuration
            deployment_config = self._generate_deployment_config(reviewed_code, requirements)
            
            # Step 7: UI Generation
            ui_code = self._generate_ui(reviewed_code, requirements)
            
            # Compile final results
            final_result = {
                'project_name': project_name,
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'requirements': requirements,
                'code': reviewed_code,
                'documentation': documentation,
                'tests': tests,
                'deployment': deployment_config,
                'ui': ui_code,
                'progress': self.progress_tracker.get_progress()
            }
            
            # Save results
            self._save_project_results(final_result)
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise
    
    def _analyze_requirements(self, user_input: str) -> Dict[str, Any]:
        """Step 1: Analyze requirements from user input."""
        self.progress_tracker.start_step(0, "requirement_analyst")
        self.progress_tracker.add_log("Starting requirements analysis", "info", "requirement_analyst")
        
        try:
            # Add substeps for detailed tracking
            self.progress_tracker.add_substep(0, "parsing_input", "Parsing user input")
            self.progress_tracker.update_substep(0, "parsing_input", "running")
            self.progress_tracker.update_step_progress(0, 10, "Parsing user input")
            
            # Create a conversation for requirements analysis
            self.progress_tracker.update_substep(0, "parsing_input", "completed")
            self.progress_tracker.add_substep(0, "analyzing_requirements", "Analyzing requirements")
            self.progress_tracker.update_substep(0, "analyzing_requirements", "running")
            self.progress_tracker.update_step_progress(0, 30, "Analyzing requirements with AI agent")
            
            chat_result = self.agents['user_proxy'].initiate_chat(
                self.agents['requirement_analyst'],
                message=f"""Please analyze the following user request and convert it into structured software requirements:

User Request: {user_input}

Please provide a comprehensive analysis including:
1. Functional requirements (specific features and capabilities)
2. Non-functional requirements (performance, security, usability)
3. Technical constraints and assumptions
4. Any clarifying questions or recommendations

Format your response as a JSON structure with the following keys:
- functional_requirements: []
- non_functional_requirements: []
- constraints: []
- assumptions: []
- questions: []
- recommendations: []
""",
                max_turns=3
            )
            
            self.progress_tracker.update_step_progress(0, 70, "Processing agent response")
            self.progress_tracker.update_substep(0, "analyzing_requirements", "completed")
            self.progress_tracker.add_substep(0, "structuring_output", "Structuring output")
            self.progress_tracker.update_substep(0, "structuring_output", "running")
            
            # Extract requirements from the conversation
            requirements_text = chat_result.chat_history[-1]['content']
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', requirements_text, re.DOTALL)
                if json_match:
                    requirements = json.loads(json_match.group())
                else:
                    # Fallback: create structured requirements from text
                    requirements = self._parse_requirements_from_text(requirements_text)
            except json.JSONDecodeError:
                requirements = self._parse_requirements_from_text(requirements_text)
            
            self.progress_tracker.update_step_progress(0, 100, "Requirements analysis completed")
            self.progress_tracker.update_substep(0, "structuring_output", "completed")
            self.progress_tracker.complete_step(0, True, "Requirements successfully analyzed and structured")
            
            return requirements
            
        except Exception as e:
            self.progress_tracker.complete_step(0, False, f"Requirements analysis failed: {str(e)}")
            raise
    
    def _generate_code(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Generate code from requirements."""
        self.progress_tracker.start_step(1, "python_coder")
        self.progress_tracker.add_log("Starting code generation", "info", "python_coder")
        
        try:
            # Add substeps for detailed tracking
            self.progress_tracker.add_substep(1, "preparing_requirements", "Preparing requirements for code generation")
            self.progress_tracker.update_substep(1, "preparing_requirements", "running")
            self.progress_tracker.update_step_progress(1, 10, "Preparing requirements")
            
            requirements_text = json.dumps(requirements, indent=2)
            
            self.progress_tracker.update_substep(1, "preparing_requirements", "completed")
            self.progress_tracker.add_substep(1, "generating_code", "Generating Python code with AI agent")
            self.progress_tracker.update_substep(1, "generating_code", "running")
            self.progress_tracker.update_step_progress(1, 25, "Generating code with AI agent")
            
            chat_result = self.agents['user_proxy'].initiate_chat(
                self.agents['python_coder'],
                message=f"""Based on the following structured requirements, please generate complete, production-ready Python code:

Requirements:
{requirements_text}

Please provide:
1. Complete Python modules with proper structure
2. All necessary imports and dependencies
3. Comprehensive docstrings and type hints
4. Error handling and logging
5. Configuration management
6. Main entry point

Structure your response with clear code blocks and explanations.""",
                max_turns=2
            )
            
            self.progress_tracker.update_step_progress(1, 70, "Processing generated code")
            self.progress_tracker.update_substep(1, "generating_code", "completed")
            self.progress_tracker.add_substep(1, "extracting_code", "Extracting code blocks")
            self.progress_tracker.update_substep(1, "extracting_code", "running")
            
            code_response = chat_result.chat_history[-1]['content']
            code_blocks = extract_code_blocks(code_response)
            
            code_result = {
                'main_code': code_blocks[0] if code_blocks else code_response,
                'additional_modules': code_blocks[1:] if len(code_blocks) > 1 else [],
                'full_response': code_response,
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.update_step_progress(1, 100, "Code generation completed")
            self.progress_tracker.update_substep(1, "extracting_code", "completed")
            self.progress_tracker.complete_step(1, True, "Python code successfully generated")
            
            return code_result
            
        except Exception as e:
            self.progress_tracker.complete_step(1, False, f"Code generation failed: {str(e)}")
            raise
    
    def _review_code(self, code_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Review and improve code."""
        self.progress_tracker.start_step(2)
        self.logger.info("Starting code review")
        
        try:
            code_to_review = code_result['main_code']
            requirements_text = json.dumps(requirements, indent=2)
            
            # Initial review
            review_result = self.agents['user_proxy'].initiate_chat(
                self.agents['code_reviewer'],
                message=f"""Please perform a comprehensive code review of the following Python code:

Original Requirements:
{requirements_text}

Code to Review:
```python
{code_to_review}
```

Please analyze:
1. Code correctness and logic
2. Security vulnerabilities
3. Performance optimization opportunities
4. Best practices adherence
5. Error handling completeness
6. Documentation quality

Provide specific feedback and suggestions for improvement.""",
                max_turns=2
            )
            
            review_feedback = review_result.chat_history[-1]['content']
            
            # If issues found, iterate with coding agent
            if any(keyword in review_feedback.lower() for keyword in ['issue', 'problem', 'fix', 'improve', 'error']):
                self.logger.info("Issues found, requesting code improvements")
                
                improvement_result = self.agents['user_proxy'].initiate_chat(
                    self.agents['python_coder'],
                    message=f"""Based on the following code review feedback, please improve the code:

Review Feedback:
{review_feedback}

Original Code:
```python
{code_to_review}
```

Please provide the improved version addressing all the feedback.""",
                    max_turns=2
                )
                
                improved_code_response = improvement_result.chat_history[-1]['content']
                improved_code_blocks = extract_code_blocks(improved_code_response)
                
                final_code = improved_code_blocks[0] if improved_code_blocks else improved_code_response
            else:
                final_code = code_to_review
            
            reviewed_result = {
                'final_code': final_code,
                'review_feedback': review_feedback,
                'original_code': code_to_review,
                'additional_modules': code_result.get('additional_modules', []),
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.complete_step(2, True)
            self.logger.info("Code review completed")
            
            return reviewed_result
            
        except Exception as e:
            self.progress_tracker.complete_step(2, False)
            self.logger.error(f"Code review failed: {str(e)}")
            raise
    
    def _generate_documentation(self, code_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Generate comprehensive documentation."""
        self.progress_tracker.start_step(3)
        self.logger.info("Starting documentation generation")
        
        try:
            final_code = code_result['final_code']
            requirements_text = json.dumps(requirements, indent=2)
            
            doc_result = self.agents['user_proxy'].initiate_chat(
                self.agents['documentation_writer'],
                message=f"""Please create comprehensive documentation for the following Python code:

Requirements:
{requirements_text}

Code:
```python
{final_code}
```

Please provide:
1. README.md with installation and usage instructions
2. API documentation with examples
3. Architecture overview
4. Configuration guide
5. Troubleshooting section

Format as markdown documents.""",
                max_turns=2
            )
            
            documentation_response = doc_result.chat_history[-1]['content']
            
            documentation = {
                'readme': documentation_response,
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.complete_step(3, True)
            self.logger.info("Documentation generation completed")
            
            return documentation
            
        except Exception as e:
            self.progress_tracker.complete_step(3, False)
            self.logger.error(f"Documentation generation failed: {str(e)}")
            raise
    
    def _generate_tests(self, code_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Generate comprehensive test cases."""
        self.progress_tracker.start_step(4)
        self.logger.info("Starting test generation")
        
        try:
            final_code = code_result['final_code']
            requirements_text = json.dumps(requirements, indent=2)
            
            test_result = self.agents['user_proxy'].initiate_chat(
                self.agents['test_generator'],
                message=f"""Please create comprehensive test cases for the following Python code:

Requirements:
{requirements_text}

Code to Test:
```python
{final_code}
```

Please provide:
1. Unit tests using pytest
2. Integration tests
3. Edge case tests
4. Mock objects for external dependencies
5. Test fixtures and setup
6. Performance tests if applicable

Ensure >90% code coverage.""",
                max_turns=2
            )
            
            test_response = test_result.chat_history[-1]['content']
            test_code_blocks = extract_code_blocks(test_response)
            
            tests = {
                'test_code': test_code_blocks[0] if test_code_blocks else test_response,
                'additional_tests': test_code_blocks[1:] if len(test_code_blocks) > 1 else [],
                'full_response': test_response,
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.complete_step(4, True)
            self.logger.info("Test generation completed")
            
            return tests
            
        except Exception as e:
            self.progress_tracker.complete_step(4, False)
            self.logger.error(f"Test generation failed: {str(e)}")
            raise
    
    def _generate_deployment_config(self, code_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Generate deployment configurations."""
        self.progress_tracker.start_step(5)
        self.logger.info("Starting deployment configuration generation")
        
        try:
            final_code = code_result['final_code']
            requirements_text = json.dumps(requirements, indent=2)
            
            deployment_result = self.agents['user_proxy'].initiate_chat(
                self.agents['deployment_engineer'],
                message=f"""Please create deployment configurations for the following Python application:

Requirements:
{requirements_text}

Application Code:
```python
{final_code}
```

Please provide:
1. Dockerfile for containerization
2. docker-compose.yml for multi-service setup
3. GitHub Actions CI/CD pipeline
4. Environment configuration files
5. Deployment scripts
6. Health check configurations

Make it production-ready and scalable.""",
                max_turns=2
            )
            
            deployment_response = deployment_result.chat_history[-1]['content']
            
            deployment = {
                'deployment_configs': deployment_response,
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.complete_step(5, True)
            self.logger.info("Deployment configuration generation completed")
            
            return deployment
            
        except Exception as e:
            self.progress_tracker.complete_step(5, False)
            self.logger.error(f"Deployment configuration generation failed: {str(e)}")
            raise
    
    def _generate_ui(self, code_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Step 7: Generate Streamlit UI."""
        self.progress_tracker.start_step(6)
        self.logger.info("Starting UI generation")
        
        try:
            final_code = code_result['final_code']
            requirements_text = json.dumps(requirements, indent=2)
            
            ui_result = self.agents['user_proxy'].initiate_chat(
                self.agents['ui_designer'],
                message=f"""Please create a Streamlit web interface for the following Python application:

Requirements:
{requirements_text}

Backend Code:
```python
{final_code}
```

Please provide:
1. Complete Streamlit application
2. Interactive forms and inputs
3. Data visualization components
4. Real-time updates and progress indicators
5. Error handling and user feedback
6. Responsive design

Make it user-friendly and professional.""",
                max_turns=2
            )
            
            ui_response = ui_result.chat_history[-1]['content']
            ui_code_blocks = extract_code_blocks(ui_response)
            
            ui = {
                'streamlit_app': ui_code_blocks[0] if ui_code_blocks else ui_response,
                'additional_ui_files': ui_code_blocks[1:] if len(ui_code_blocks) > 1 else [],
                'full_response': ui_response,
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.complete_step(6, True)
            self.logger.info("UI generation completed")
            
            return ui
            
        except Exception as e:
            self.progress_tracker.complete_step(6, False)
            self.logger.error(f"UI generation failed: {str(e)}")
            raise
    
    def _parse_requirements_from_text(self, text: str) -> Dict[str, Any]:
        """Parse requirements from text when JSON parsing fails."""
        return {
            'functional_requirements': [text],
            'non_functional_requirements': [],
            'constraints': [],
            'assumptions': [],
            'questions': [],
            'recommendations': []
        }
    
    def _save_project_results(self, results: Dict[str, Any]) -> None:
        """Save all project results to files."""
        project_name = results['project_name']
        timestamp = generate_timestamp()
        
        # Create project directory
        project_dir = f"{self.output_dir}/{project_name}_{timestamp}"
        
        # Save main results as JSON
        save_json(results, f"{project_dir}/project_results.json")
        
        # Save individual components
        save_text(results['code']['final_code'], f"{project_dir}/main.py")
        save_text(results['documentation']['readme'], f"{project_dir}/README.md")
        save_text(results['tests']['test_code'], f"{project_dir}/test_main.py")
        save_text(results['ui']['streamlit_app'], f"{project_dir}/streamlit_app.py")
        save_text(results['deployment']['deployment_configs'], f"{project_dir}/deployment.md")
        
        self.logger.info(f"Project results saved to {project_dir}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress status."""
        return self.progress_tracker.get_progress()
    
    def reset_progress(self) -> None:
        """Reset progress tracker for new project."""
        self.progress_tracker = ProgressTracker()
        self._setup_progress_steps()
