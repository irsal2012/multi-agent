"""
Agent Manager for coordinating multiple AutoGen agents.
"""

import json
import logging
import time
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
from core.loop_progress_tracker import LoopProgressTracker

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
        """Process user input through the complete agent pipeline with robust error handling."""
        if not project_name:
            project_name = f"project_{generate_timestamp()}"
        
        self.current_project = project_name
        self.logger.info(f"Starting resilient pipeline for project: {project_name}")
        
        # Initialize results with defaults to ensure we always have something to return
        pipeline_results = {
            'project_name': project_name,
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'requirements': None,
            'code': None,
            'documentation': None,
            'tests': None,
            'deployment': None,
            'ui': None,
            'pipeline_status': {
                'completed_steps': [],
                'failed_steps': [],
                'warnings': [],
                'has_partial_results': False,
                'overall_success': False
            }
        }
        
        # Step 1: Requirements Analysis (Critical - must succeed)
        requirements = self._execute_step_with_resilience(
            step_name="requirements_analysis",
            step_function=lambda: self._analyze_requirements(user_input),
            fallback_function=lambda: self._create_fallback_requirements(user_input),
            pipeline_results=pipeline_results,
            is_critical=True
        )
        pipeline_results['requirements'] = requirements
        
        # Step 2: Code Generation (Critical - must succeed)
        code_result = self._execute_step_with_resilience(
            step_name="code_generation",
            step_function=lambda: self._generate_code(requirements),
            fallback_function=lambda: self._create_fallback_code(requirements),
            pipeline_results=pipeline_results,
            is_critical=True
        )
        pipeline_results['code'] = code_result
        
        # Step 3: Code Review (Important but not critical)
        reviewed_code = self._execute_step_with_resilience(
            step_name="code_review",
            step_function=lambda: self._review_code(code_result, requirements),
            fallback_function=lambda: self._create_fallback_review(code_result),
            pipeline_results=pipeline_results,
            is_critical=False
        )
        pipeline_results['code'] = reviewed_code or code_result
        
        # Step 4: Documentation Generation (Optional)
        documentation = self._execute_step_with_resilience(
            step_name="documentation",
            step_function=lambda: self._generate_documentation(pipeline_results['code'], requirements),
            fallback_function=lambda: self._create_fallback_documentation(pipeline_results['code'], requirements),
            pipeline_results=pipeline_results,
            is_critical=False
        )
        pipeline_results['documentation'] = documentation
        
        # Step 5: Test Generation (Optional)
        tests = self._execute_step_with_resilience(
            step_name="test_generation",
            step_function=lambda: self._generate_tests(pipeline_results['code'], requirements),
            fallback_function=lambda: self._create_fallback_tests(pipeline_results['code']),
            pipeline_results=pipeline_results,
            is_critical=False
        )
        pipeline_results['tests'] = tests
        
        # Step 6: Deployment Configuration (Optional)
        deployment_config = self._execute_step_with_resilience(
            step_name="deployment_config",
            step_function=lambda: self._generate_deployment_config(pipeline_results['code'], requirements),
            fallback_function=lambda: self._create_fallback_deployment(pipeline_results['code']),
            pipeline_results=pipeline_results,
            is_critical=False
        )
        pipeline_results['deployment'] = deployment_config
        
        # Step 7: UI Generation (Optional but important)
        ui_code = self._execute_step_with_resilience(
            step_name="ui_generation",
            step_function=lambda: self._generate_ui(pipeline_results['code'], requirements),
            fallback_function=lambda: self._create_fallback_ui_result(requirements, pipeline_results['code']),
            pipeline_results=pipeline_results,
            is_critical=False
        )
        pipeline_results['ui'] = ui_code
        
        # Finalize results
        pipeline_results['progress'] = self.progress_tracker.get_progress()
        pipeline_results['pipeline_status']['overall_success'] = len(pipeline_results['pipeline_status']['failed_steps']) == 0
        pipeline_results['pipeline_status']['has_partial_results'] = len(pipeline_results['pipeline_status']['completed_steps']) > 0
        
        # Always save results, even if partial
        try:
            self._save_project_results(pipeline_results)
        except Exception as save_error:
            self.logger.warning(f"Failed to save results: {str(save_error)}")
            pipeline_results['pipeline_status']['warnings'].append(f"Results saving failed: {str(save_error)}")
        
        # Log final status
        completed_count = len(pipeline_results['pipeline_status']['completed_steps'])
        failed_count = len(pipeline_results['pipeline_status']['failed_steps'])
        self.logger.info(f"Pipeline completed: {completed_count} steps succeeded, {failed_count} steps failed")
        
        return pipeline_results
    
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
        """Step 3: Review and improve code with loop visualization."""
        self.progress_tracker.start_step(2)
        self.logger.info("Starting code review with loop tracking")
        
        try:
            # Use the enhanced loop-based review process
            return self._review_code_with_loop(code_result, requirements)
            
        except Exception as e:
            self.progress_tracker.complete_step(2, False)
            self.logger.error(f"Code review failed: {str(e)}")
            raise
    
    def _review_code_with_loop(self, code_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced code review with iterative generation-review loop."""
        
        # Initialize loop tracker
        loop_tracker = LoopProgressTracker(
            convergence_threshold=0.85,  # 85% quality threshold
            max_iterations=3  # Maximum 3 iterations
        )
        
        # Store loop tracker for external access (e.g., UI)
        self.current_loop_tracker = loop_tracker
        
        code_to_review = code_result['main_code']
        requirements_text = json.dumps(requirements, indent=2)
        current_code = code_to_review
        
        # Start the loop
        loop_tracker.start_loop()
        
        try:
            while loop_tracker.should_continue_loop():
                current_iteration = loop_tracker.current_iteration
                
                # Ensure we have a current iteration
                if not current_iteration:
                    self.logger.error("No current iteration available")
                    break
                
                # Generation Phase
                self.logger.info(f"Starting generation phase for iteration {current_iteration.iteration_number}")
                
                if current_iteration.iteration_number == 1:
                    # First iteration: use the initial code
                    loop_tracker.update_generation_progress(10, "Using initial generated code")
                    time.sleep(0.5)  # Small delay for UI updates
                    loop_tracker.update_generation_progress(50, "Processing initial code structure")
                    time.sleep(0.5)
                    loop_tracker.update_generation_progress(100, "Initial code ready for review")
                    
                    # Calculate initial quality score
                    quality_score = 0.6  # Starting quality
                    loop_tracker.complete_generation(quality_score)
                else:
                    # Subsequent iterations: improve based on feedback
                    loop_tracker.update_generation_progress(10, "Analyzing feedback from previous review")
                    time.sleep(0.5)
                    
                    # Get feedback from previous iteration
                    previous_iteration = loop_tracker.iterations[-2] if len(loop_tracker.iterations) >= 2 else None
                    previous_feedback = previous_iteration.feedback if previous_iteration else []
                    feedback_text = "\n".join(previous_feedback) if previous_feedback else "No specific feedback"
                    
                    loop_tracker.update_generation_progress(30, "Generating improved code based on feedback")
                    
                    try:
                        # Generate improved code based on feedback
                        improvement_result = self.agents['user_proxy'].initiate_chat(
                            self.agents['python_coder'],
                            message=f"""Based on the following code review feedback, please improve the code:

Review Feedback:
{feedback_text}

Current Code:
```python
{current_code}
```

Original Requirements:
{requirements_text}

Please provide an improved version that addresses all the feedback while maintaining the original requirements.""",
                            max_turns=2
                        )
                        
                        loop_tracker.update_generation_progress(70, "Processing improved code")
                        
                        improved_code_response = improvement_result.chat_history[-1]['content']
                        improved_code_blocks = extract_code_blocks(improved_code_response)
                        current_code = improved_code_blocks[0] if improved_code_blocks else improved_code_response
                        
                        loop_tracker.update_generation_progress(100, "Code generation completed")
                        
                        # Calculate quality score based on iteration
                        quality_score = min(0.6 + (current_iteration.iteration_number * 0.1), 1.0)
                        loop_tracker.complete_generation(quality_score)
                        
                    except Exception as gen_error:
                        self.logger.error(f"Generation failed: {str(gen_error)}")
                        loop_tracker.fail_loop(f"Generation failed: {str(gen_error)}")
                        break
                
                # Wait for review phase to start (complete_generation should have started it)
                if loop_tracker.current_state.value != "review":
                    self.logger.error(f"Expected review state, got {loop_tracker.current_state.value}")
                    break
                
                # Review Phase
                self.logger.info(f"Starting review phase for iteration {current_iteration.iteration_number}")
                
                loop_tracker.update_review_progress(10, "Starting comprehensive code review")
                
                try:
                    review_result = self.agents['user_proxy'].initiate_chat(
                        self.agents['code_reviewer'],
                        message=f"""Please perform a comprehensive code review of the following Python code:

Original Requirements:
{requirements_text}

Code to Review (Iteration #{current_iteration.iteration_number}):
```python
{current_code}
```

Please analyze:
1. Code correctness and logic
2. Security vulnerabilities  
3. Performance optimization opportunities
4. Best practices adherence
5. Error handling completeness
6. Documentation quality

Provide specific, actionable feedback. Rate the overall code quality on a scale of 0.0 to 1.0.
If the code quality is above 0.85, indicate that it's ready for production.
Format your response with:
- QUALITY_SCORE: [0.0-1.0]
- FEEDBACK: [specific improvements needed]
- STATUS: [READY/NEEDS_IMPROVEMENT]""",
                        max_turns=2
                    )
                    
                    loop_tracker.update_review_progress(50, "Analyzing code quality and generating feedback")
                    
                    review_response = review_result.chat_history[-1]['content']
                    
                    # Parse review response
                    quality_score, feedback_items, is_ready = self._parse_review_response(review_response)
                    
                    loop_tracker.update_review_progress(80, "Processing review feedback")
                    
                    # Add feedback to tracker
                    for feedback in feedback_items:
                        loop_tracker.add_feedback(feedback)
                    
                    loop_tracker.update_review_progress(100, "Review completed")
                    
                    # Calculate convergence score
                    convergence_score = quality_score
                    
                    # Complete the review phase - this will determine if we continue or finish
                    loop_tracker.complete_review(convergence_score)
                    
                    # Update progress tracker
                    loop_progress = loop_tracker.get_convergence_progress()
                    self.progress_tracker.update_step_progress(2, loop_progress, 
                        f"Loop iteration #{current_iteration.iteration_number} completed")
                    
                except Exception as review_error:
                    self.logger.error(f"Review failed: {str(review_error)}")
                    loop_tracker.fail_loop(f"Review failed: {str(review_error)}")
                    break
                
                # Check if loop should continue
                if not loop_tracker.should_continue_loop():
                    self.logger.info("Loop convergence achieved or max iterations reached")
                    break
            
            # Loop completed - compile final results
            final_iteration = loop_tracker.iterations[-1] if loop_tracker.iterations else None
            
            reviewed_result = {
                'final_code': current_code,
                'review_feedback': loop_tracker.get_recent_logs(10),
                'original_code': code_to_review,
                'additional_modules': code_result.get('additional_modules', []),
                'loop_summary': {
                    'total_iterations': len(loop_tracker.iterations),
                    'final_quality_score': final_iteration.quality_score if final_iteration else 0.0,
                    'final_convergence_score': final_iteration.convergence_score if final_iteration else 0.0,
                    'total_feedback_items': sum(len(it.feedback) for it in loop_tracker.iterations),
                    'loop_duration': loop_tracker.get_total_duration()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.complete_step(2, True, 
                f"Code review completed after {len(loop_tracker.iterations)} iterations")
            self.logger.info(f"Code review loop completed with {len(loop_tracker.iterations)} iterations")
            
            return reviewed_result
            
        except Exception as e:
            self.logger.error(f"Loop failed with error: {str(e)}")
            loop_tracker.fail_loop(str(e))
            raise
    
    def _parse_review_response(self, review_response: str) -> Tuple[float, List[str], bool]:
        """Parse the review response to extract quality score and feedback."""
        import re
        
        # Extract quality score
        quality_match = re.search(r'QUALITY_SCORE:\s*([0-9.]+)', review_response)
        quality_score = float(quality_match.group(1)) if quality_match else 0.7
        
        # Extract status
        status_match = re.search(r'STATUS:\s*(READY|NEEDS_IMPROVEMENT)', review_response)
        is_ready = status_match and status_match.group(1) == 'READY'
        
        # Extract feedback items
        feedback_section = re.search(r'FEEDBACK:\s*(.*?)(?=STATUS:|$)', review_response, re.DOTALL)
        if feedback_section:
            feedback_text = feedback_section.group(1).strip()
            # Split into individual feedback items
            feedback_items = [item.strip() for item in feedback_text.split('\n') if item.strip() and not item.strip().startswith('-')]
            # Clean up feedback items
            feedback_items = [item.lstrip('- ').strip() for item in feedback_items if len(item.strip()) > 10]
        else:
            # Fallback: extract general feedback
            feedback_items = []
            lines = review_response.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['improve', 'fix', 'add', 'consider', 'should']):
                    feedback_items.append(line.strip())
        
        return quality_score, feedback_items[:5], is_ready  # Limit to 5 feedback items
    
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
        """Step 7: Generate Streamlit UI with enhanced error handling and recovery."""
        self.progress_tracker.start_step(6, "ui_designer")
        self.progress_tracker.add_log("Starting UI generation with thread-safe error handling", "info", "ui_designer")
        
        # Initialize variables for cleanup
        ui_result = None
        ui_response = ""
        ui_code_blocks = []
        
        try:
            # Add substeps for detailed tracking
            self.progress_tracker.add_substep(6, "preparing_ui_requirements", "Preparing UI requirements")
            self.progress_tracker.update_substep(6, "preparing_ui_requirements", "running")
            self.progress_tracker.update_step_progress(6, 10, "Preparing UI requirements")
            
            # Add small delay to ensure progress is visible
            import time
            time.sleep(0.5)
            
            final_code = code_result.get('final_code', '')
            if not final_code:
                raise ValueError("No final code available for UI generation")
            
            requirements_text = json.dumps(requirements, indent=2)
            
            # Validate requirements
            if not requirements or not isinstance(requirements, dict):
                self.logger.warning("Invalid requirements format, using fallback")
                requirements_text = json.dumps({"functional_requirements": ["Create a basic UI"]}, indent=2)
            
            self.progress_tracker.update_substep(6, "preparing_ui_requirements", "completed")
            self.progress_tracker.add_substep(6, "generating_ui", "Generating Streamlit UI with AI agent")
            self.progress_tracker.update_substep(6, "generating_ui", "running")
            self.progress_tracker.update_step_progress(6, 25, "Generating UI with AI agent")
            
            # Add progress update during AI generation
            time.sleep(0.5)
            self.progress_tracker.update_step_progress(6, 35, "Communicating with UI designer agent")
            
            # Enhanced UI generation with thread-safe timeout and retry logic
            max_retries = 2
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    self.logger.info(f"UI generation attempt {retry_count + 1}/{max_retries + 1}")
                    
                    # Create a more focused prompt to reduce processing time
                    ui_prompt = self._create_focused_ui_prompt(requirements_text, final_code, retry_count)
                    
                    # Use thread-safe timeout mechanism instead of signal
                    ui_result = self._run_ui_generation_with_timeout(
                        ui_prompt, 
                        timeout_seconds=90,
                        max_turns=1 if retry_count > 0 else 2
                    )
                    
                    if ui_result:
                        break  # Success, exit retry loop
                    else:
                        raise Exception("UI generation returned no result")
                        
                except TimeoutError:
                    self.logger.warning(f"UI generation timed out on attempt {retry_count + 1}")
                    if retry_count == max_retries:
                        raise TimeoutError("UI generation timed out after all retries")
                    retry_count += 1
                    time.sleep(2)  # Brief pause before retry
                    continue
                        
                except Exception as gen_error:
                    self.logger.warning(f"UI generation attempt {retry_count + 1} failed: {str(gen_error)}")
                    if retry_count == max_retries:
                        raise gen_error
                    retry_count += 1
                    time.sleep(2)  # Brief pause before retry
                    continue
            
            if not ui_result:
                raise Exception("Failed to generate UI after all retry attempts")
            
            self.progress_tracker.update_step_progress(6, 70, "Processing generated UI code")
            self.progress_tracker.update_substep(6, "generating_ui", "completed")
            self.progress_tracker.add_substep(6, "extracting_ui_code", "Extracting UI code blocks")
            self.progress_tracker.update_substep(6, "extracting_ui_code", "running")
            
            time.sleep(0.3)
            self.progress_tracker.update_step_progress(6, 85, "Extracting and validating UI code")
            
            # Safe extraction of UI response
            try:
                ui_response = ui_result.chat_history[-1]['content'] if ui_result.chat_history else ""
            except (IndexError, KeyError, AttributeError) as e:
                self.logger.warning(f"Failed to extract UI response: {str(e)}")
                ui_response = ""
            
            # Extract code blocks with error handling
            try:
                ui_code_blocks = extract_code_blocks(ui_response) if ui_response else []
            except Exception as e:
                self.logger.warning(f"Failed to extract code blocks: {str(e)}")
                ui_code_blocks = []
            
            # Validate that we have UI code or create fallback
            if not ui_code_blocks and not ui_response.strip():
                self.logger.warning("No UI code generated, creating fallback UI")
                fallback_ui = self._create_fallback_ui(requirements, final_code)
                ui_code_blocks = [fallback_ui]
                ui_response = f"# Fallback UI Generated\n\n```python\n{fallback_ui}\n```"
            
            # Final validation
            main_ui_code = ui_code_blocks[0] if ui_code_blocks else ui_response
            if not main_ui_code or len(main_ui_code.strip()) < 50:
                self.logger.warning("Generated UI code is too short, enhancing with fallback")
                fallback_ui = self._create_fallback_ui(requirements, final_code)
                main_ui_code = fallback_ui
            
            ui = {
                'streamlit_app': main_ui_code,
                'additional_ui_files': ui_code_blocks[1:] if len(ui_code_blocks) > 1 else [],
                'full_response': ui_response,
                'generation_metadata': {
                    'retry_count': retry_count,
                    'generation_method': 'ai_generated' if ui_code_blocks else 'fallback',
                    'code_blocks_found': len(ui_code_blocks),
                    'response_length': len(ui_response)
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_tracker.update_step_progress(6, 100, "UI generation completed")
            self.progress_tracker.update_substep(6, "extracting_ui_code", "completed")
            self.progress_tracker.complete_step(6, True, f"Streamlit UI successfully generated (method: {ui['generation_metadata']['generation_method']})")
            
            self.logger.info(f"UI generation completed successfully. Generated {len(ui_code_blocks)} code blocks using {ui['generation_metadata']['generation_method']} method.")
            
            return ui
            
        except Exception as e:
            self.logger.error(f"UI generation failed: {str(e)}")
            
            # Attempt to create emergency fallback UI
            try:
                self.logger.info("Attempting to create emergency fallback UI")
                fallback_ui = self._create_fallback_ui(requirements, code_result.get('final_code', ''))
                
                emergency_ui = {
                    'streamlit_app': fallback_ui,
                    'additional_ui_files': [],
                    'full_response': f"# Emergency Fallback UI\n\nGenerated due to error: {str(e)}",
                    'generation_metadata': {
                        'retry_count': 0,
                        'generation_method': 'emergency_fallback',
                        'error': str(e),
                        'code_blocks_found': 1,
                        'response_length': len(fallback_ui)
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                self.progress_tracker.complete_step(6, True, f"Emergency fallback UI created due to error: {str(e)}")
                self.logger.info("Emergency fallback UI created successfully")
                
                return emergency_ui
                
            except Exception as fallback_error:
                self.logger.error(f"Emergency fallback UI creation also failed: {str(fallback_error)}")
                self.progress_tracker.complete_step(6, False, f"UI generation and fallback failed: {str(e)}")
                raise Exception(f"UI generation failed and fallback creation failed: {str(e)}")
    
    def _run_ui_generation_with_timeout(self, ui_prompt: str, timeout_seconds: int = 90, max_turns: int = 2) -> Optional[Any]:
        """Run UI generation with thread-safe timeout mechanism."""
        import threading
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        result = None
        exception = None
        
        def run_generation():
            """Run the actual UI generation in a separate thread."""
            nonlocal result, exception
            try:
                self.logger.debug("Starting UI generation chat")
                result = self.agents['user_proxy'].initiate_chat(
                    self.agents['ui_designer'],
                    message=ui_prompt,
                    max_turns=max_turns
                )
                self.logger.debug("UI generation chat completed successfully")
            except Exception as e:
                self.logger.error(f"UI generation chat failed: {str(e)}")
                exception = e
        
        try:
            # Use ThreadPoolExecutor for timeout control
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_generation)
                
                try:
                    # Wait for completion with timeout
                    future.result(timeout=timeout_seconds)
                    
                    if exception:
                        raise exception
                    
                    return result
                    
                except FutureTimeoutError:
                    self.logger.warning(f"UI generation timed out after {timeout_seconds} seconds")
                    raise TimeoutError(f"UI generation timed out after {timeout_seconds} seconds")
                    
        except Exception as e:
            self.logger.error(f"Thread-safe UI generation failed: {str(e)}")
            raise e
    
    def _create_focused_ui_prompt(self, requirements_text: str, final_code: str, retry_count: int) -> str:
        """Create a focused UI generation prompt based on retry count."""
        if retry_count == 0:
            # First attempt: comprehensive prompt
            return f"""Please create a Streamlit web interface for the following Python application:

Requirements:
{requirements_text}

Backend Code:
```python
{final_code[:2000]}{'...' if len(final_code) > 2000 else ''}
```

Please provide:
1. Complete Streamlit application with proper imports
2. Interactive forms and inputs for user interaction
3. Data visualization components (charts, tables, etc.)
4. Real-time updates and progress indicators
5. Error handling and user feedback messages
6. Responsive design with proper layout
7. Navigation and user-friendly interface

Structure your response with clear code blocks and explanations.
Make it user-friendly, professional, and fully functional."""
        else:
            # Retry attempt: simplified prompt
            return f"""Create a simple Streamlit interface for this Python application:

Requirements: {requirements_text[:500]}{'...' if len(requirements_text) > 500 else ''}

Code: 
```python
{final_code[:1000]}{'...' if len(final_code) > 1000 else ''}
```

Provide a basic but functional Streamlit app with:
1. Main interface with title and description
2. Input forms for user interaction
3. Display area for results
4. Basic error handling

Keep it simple and functional."""
    
    def _create_fallback_ui(self, requirements: Dict[str, Any], final_code: str) -> str:
        """Create a fallback UI when AI generation fails."""
        app_name = "Generated Application"
        
        # Extract some basic info from requirements
        functional_reqs = requirements.get('functional_requirements', [])
        description = functional_reqs[0] if functional_reqs else "A Python application with web interface"
        
        # Create a basic but functional Streamlit app
        fallback_ui = f'''import streamlit as st
import json
import traceback
from typing import Dict, Any

# Configure page
st.set_page_config(
    page_title="{app_name}",
    page_icon="🚀",
    layout="wide"
)

def main():
    """Main application interface."""
    st.title("🚀 {app_name}")
    st.markdown("""
    {description}
    
    This is a fallback interface generated when the AI-powered UI generation encountered issues.
    The interface provides basic functionality to interact with the underlying application.
    """)
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Choose a section:", ["Main", "Settings", "About"])
    
    if page == "Main":
        show_main_interface()
    elif page == "Settings":
        show_settings()
    else:
        show_about()

def show_main_interface():
    """Main application interface."""
    st.header("Main Interface")
    
    # Input section
    with st.expander("Input", expanded=True):
        user_input = st.text_area(
            "Enter your input:",
            placeholder="Type your input here...",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Process", type="primary"):
                if user_input:
                    process_input(user_input)
                else:
                    st.error("Please enter some input")
    
    # Results section
    st.header("Results")
    if 'results' in st.session_state:
        st.success("Processing completed!")
        st.json(st.session_state.results)
    else:
        st.info("No results yet. Enter input above and click Process.")

def process_input(user_input: str):
    """Process user input with the underlying application."""
    try:
        # This is where you would integrate with the actual generated code
        # For now, we'll create a placeholder result
        result = {{
            "input": user_input,
            "processed": True,
            "message": "Input processed successfully",
            "timestamp": str(st.session_state.get('timestamp', 'N/A'))
        }}
        
        st.session_state.results = result
        st.rerun()
        
    except Exception as e:
        st.error(f"Processing failed: {{str(e)}}")
        st.code(traceback.format_exc())

def show_settings():
    """Settings page."""
    st.header("Settings")
    st.info("Settings functionality can be customized based on your application needs.")
    
    # Example settings
    debug_mode = st.checkbox("Debug Mode", value=False)
    if debug_mode:
        st.subheader("Debug Information")
        st.code("""
# Generated Code Preview:
{final_code[:500]}{'...' if len(final_code) > 500 else ''}
        """)

def show_about():
    """About page."""
    st.header("About")
    st.markdown("""
    This application was generated using a multi-agent AI framework.
    
    **Features:**
    - Automated code generation
    - Comprehensive testing
    - Documentation generation
    - Deployment configuration
    - Web interface (this page)
    
    **Note:** This is a fallback interface created when the primary UI generation encountered issues.
    The underlying functionality remains intact and can be accessed through this interface.
    """)

if __name__ == "__main__":
    main()
'''
        
        return fallback_ui
    
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
        """Get current progress status with proper formatting for progress service."""
        try:
            raw_progress = self.progress_tracker.get_progress()
            
            # Convert to format expected by progress service
            formatted_progress = {
                'total_steps': raw_progress.get('total_steps', 7),
                'completed_steps': raw_progress.get('completed_steps', 0),
                'failed_steps': raw_progress.get('failed_steps', 0),
                'progress_percentage': raw_progress.get('progress_percentage', 0.0),
                'steps': self._format_steps_for_service(raw_progress.get('steps', [])),
                'elapsed_time': raw_progress.get('elapsed_time', 0.0),
                'estimated_remaining_time': raw_progress.get('estimated_remaining_time', 0.0),
                'is_running': raw_progress.get('is_running', False),
                'is_completed': raw_progress.get('is_completed', False),
                'has_failures': raw_progress.get('has_failures', False),
                'current_step_info': self._format_current_step_info(raw_progress.get('current_step_info')),
                'logs': self._format_logs_for_service(raw_progress.get('logs', []))
            }
            
            return formatted_progress
            
        except Exception as e:
            self.logger.error(f"Error getting progress: {str(e)}")
            # Return a safe default progress state
            return {
                'total_steps': 7,
                'completed_steps': 0,
                'failed_steps': 0,
                'progress_percentage': 0.0,
                'steps': [],
                'elapsed_time': 0.0,
                'estimated_remaining_time': 0.0,
                'is_running': False,
                'is_completed': False,
                'has_failures': False,
                'current_step_info': None,
                'logs': []
            }
    
    def _format_steps_for_service(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format steps for progress service compatibility."""
        formatted_steps = []
        
        for step in steps:
            formatted_step = {
                'name': step.get('name', ''),
                'description': step.get('description', ''),
                'status': step.get('status', 'pending'),
                'progress_percentage': step.get('progress_percentage', 0.0),
                'start_time': step.get('start_time'),
                'end_time': step.get('end_time'),
                'duration': step.get('duration'),
                'agent_name': step.get('agent_name'),
                'substeps': step.get('substeps', [])
            }
            formatted_steps.append(formatted_step)
        
        return formatted_steps
    
    def _format_current_step_info(self, current_step_info: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Format current step info for progress service."""
        if not current_step_info:
            return None
        
        return {
            'name': current_step_info.get('name', ''),
            'description': current_step_info.get('description', ''),
            'status': current_step_info.get('status', 'pending'),
            'progress_percentage': current_step_info.get('progress_percentage', 0.0),
            'start_time': current_step_info.get('start_time'),
            'end_time': current_step_info.get('end_time'),
            'duration': current_step_info.get('duration'),
            'agent_name': current_step_info.get('agent_name'),
            'substeps': current_step_info.get('substeps', [])
        }
    
    def _format_logs_for_service(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format logs for progress service compatibility."""
        formatted_logs = []
        
        for log in logs:
            formatted_log = {
                'timestamp': log.get('timestamp'),
                'level': log.get('level', 'INFO').upper(),
                'message': log.get('message', ''),
                'agent': log.get('agent_name'),
                'step': None,  # Can be enhanced later
                'metadata': {}
            }
            formatted_logs.append(formatted_log)
        
        return formatted_logs
    
    def get_loop_tracker(self) -> Optional[LoopProgressTracker]:
        """Get the current loop progress tracker if available."""
        return getattr(self, 'current_loop_tracker', None)
    
    def reset_progress(self) -> None:
        """Reset progress tracker for new project."""
        self.progress_tracker = ProgressTracker()
        self._setup_progress_steps()
        # Clear any existing loop tracker
        if hasattr(self, 'current_loop_tracker'):
            delattr(self, 'current_loop_tracker')
    
    def _execute_step_with_resilience(self, step_name: str, step_function, fallback_function, 
                                    pipeline_results: Dict[str, Any], is_critical: bool = False) -> Any:
        """Execute a pipeline step with resilience and fallback handling."""
        self.logger.info(f"Executing step: {step_name} (critical: {is_critical})")
        
        try:
            # Attempt to execute the main step function
            result = step_function()
            
            # Mark step as completed
            pipeline_results['pipeline_status']['completed_steps'].append(step_name)
            self.logger.info(f"Step {step_name} completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Step {step_name} failed: {error_msg}")
            
            # Check if this is an agent limit error (max_consecutive_auto_reply)
            is_agent_limit_error = self._is_agent_limit_error(error_msg)
            
            if is_agent_limit_error:
                self.logger.warning(f"Step {step_name} hit agent limit, attempting graceful degradation")
                pipeline_results['pipeline_status']['warnings'].append(
                    f"{step_name}: Agent hit max_consecutive_auto_reply limit"
                )
            
            # Try fallback function
            try:
                self.logger.info(f"Attempting fallback for step: {step_name}")
                fallback_result = fallback_function()
                
                # Mark as completed with warning
                pipeline_results['pipeline_status']['completed_steps'].append(f"{step_name}_fallback")
                pipeline_results['pipeline_status']['warnings'].append(
                    f"{step_name}: Completed using fallback due to: {error_msg}"
                )
                
                self.logger.info(f"Step {step_name} completed using fallback")
                return fallback_result
                
            except Exception as fallback_error:
                self.logger.error(f"Fallback for step {step_name} also failed: {str(fallback_error)}")
                
                # Mark step as failed
                pipeline_results['pipeline_status']['failed_steps'].append(step_name)
                
                if is_critical:
                    # For critical steps, we must have some result
                    self.logger.error(f"Critical step {step_name} failed completely, creating minimal fallback")
                    minimal_result = self._create_minimal_fallback(step_name, pipeline_results)
                    pipeline_results['pipeline_status']['warnings'].append(
                        f"{step_name}: Using minimal fallback due to complete failure"
                    )
                    return minimal_result
                else:
                    # For non-critical steps, we can continue without this result
                    self.logger.warning(f"Non-critical step {step_name} failed, continuing pipeline")
                    pipeline_results['pipeline_status']['warnings'].append(
                        f"{step_name}: Skipped due to failure: {error_msg}"
                    )
                    return None
    
    def _is_agent_limit_error(self, error_msg: str) -> bool:
        """Check if the error is related to agent limits."""
        limit_indicators = [
            "max_consecutive_auto_reply",
            "Maximum number of consecutive auto-replies",
            "TERMINATING RUN",
            "auto-reply limit",
            "consecutive replies"
        ]
        
        error_lower = error_msg.lower()
        return any(indicator.lower() in error_lower for indicator in limit_indicators)
    
    def _create_minimal_fallback(self, step_name: str, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create minimal fallback results for critical steps."""
        if step_name == "requirements_analysis":
            return self._create_fallback_requirements(pipeline_results.get('user_input', ''))
        elif step_name == "code_generation":
            return self._create_fallback_code(pipeline_results.get('requirements', {}))
        else:
            return {
                'error': f"Step {step_name} failed completely",
                'fallback_used': True,
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_fallback_requirements(self, user_input: str) -> Dict[str, Any]:
        """Create fallback requirements when AI analysis fails."""
        self.logger.info("Creating fallback requirements")
        
        return {
            'functional_requirements': [
                f"Implement functionality based on: {user_input[:200]}{'...' if len(user_input) > 200 else ''}",
                "Provide basic user interface",
                "Handle user input and provide output",
                "Include error handling"
            ],
            'non_functional_requirements': [
                "Should be reliable and user-friendly",
                "Should handle errors gracefully",
                "Should provide clear feedback to users"
            ],
            'constraints': [
                "Python-based implementation",
                "Use standard libraries where possible"
            ],
            'assumptions': [
                "User has basic Python environment",
                "Standard web browser available for UI"
            ],
            'questions': [],
            'recommendations': [
                "Consider adding logging for debugging",
                "Implement comprehensive error handling"
            ],
            'fallback_used': True,
            'original_input': user_input,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_code(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback code when AI generation fails."""
        self.logger.info("Creating fallback code")
        
        functional_reqs = requirements.get('functional_requirements', [])
        main_functionality = functional_reqs[0] if functional_reqs else "Basic functionality"
        
        fallback_code = f'''#!/usr/bin/env python3
"""
Fallback implementation generated when AI code generation failed.
Based on requirements: {main_functionality}
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Application:
    """Main application class - fallback implementation."""
    
    def __init__(self):
        """Initialize the application."""
        self.logger = logger
        self.logger.info("Application initialized (fallback mode)")
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return results."""
        try:
            self.logger.info(f"Processing input: {{user_input[:50]}}...")
            
            # Basic processing logic
            result = {{
                "input": user_input,
                "processed": True,
                "message": "Input processed successfully using fallback implementation",
                "timestamp": datetime.now().isoformat(),
                "method": "fallback"
            }}
            
            self.logger.info("Input processed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing input: {{str(e)}}")
            return {{
                "input": user_input,
                "processed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "method": "fallback"
            }}
    
    def run(self):
        """Run the application."""
        self.logger.info("Starting application (fallback mode)")
        
        try:
            # Basic interactive loop
            while True:
                user_input = input("Enter input (or 'quit' to exit): ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                result = self.process_input(user_input)
                print(f"Result: {{result}}")
                
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Application error: {{str(e)}}")
        finally:
            self.logger.info("Application shutting down")

def main():
    """Main entry point."""
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
'''
        
        return {
            'main_code': fallback_code,
            'additional_modules': [],
            'full_response': f"# Fallback Code Generated\\n\\nThis code was generated as a fallback when AI code generation failed.\\n\\n```python\\n{fallback_code}\\n```",
            'fallback_used': True,
            'requirements_used': requirements,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_review(self, code_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback review when AI review fails."""
        self.logger.info("Creating fallback code review")
        
        return {
            'final_code': code_result.get('main_code', ''),
            'review_feedback': [
                "Code review completed using fallback method",
                "Manual review recommended for production use",
                "Basic structure appears functional"
            ],
            'original_code': code_result.get('main_code', ''),
            'additional_modules': code_result.get('additional_modules', []),
            'loop_summary': {
                'total_iterations': 1,
                'final_quality_score': 0.7,
                'final_convergence_score': 0.7,
                'total_feedback_items': 1,
                'loop_duration': 0.0
            },
            'fallback_used': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_documentation(self, code_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback documentation when AI generation fails."""
        self.logger.info("Creating fallback documentation")
        
        app_name = "Generated Application"
        functional_reqs = requirements.get('functional_requirements', [])
        main_functionality = functional_reqs[0] if functional_reqs else "Basic functionality"
        
        fallback_readme = f'''# {app_name}

## Overview
{main_functionality}

This documentation was generated using a fallback method when AI documentation generation failed.

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```python
python main.py
```

### Features
- Basic functionality as specified in requirements
- Error handling and logging
- User-friendly interface

## Configuration
The application uses default configuration. Modify the code directly for custom settings.

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure all dependencies are installed
- **Runtime Errors**: Check logs for detailed error messages
- **Performance Issues**: Consider optimizing based on your specific use case

## Support
This is a generated application. For support, refer to the code comments and logs.

## License
Generated code - please add appropriate license as needed.
'''
        
        return {
            'readme': fallback_readme,
            'fallback_used': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_tests(self, code_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback tests when AI generation fails."""
        self.logger.info("Creating fallback tests")
        
        fallback_test_code = '''#!/usr/bin/env python3
"""
Fallback test suite generated when AI test generation failed.
"""

import unittest
import sys
import os

# Add the main module to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestApplication(unittest.TestCase):
    """Basic test cases for the application."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import your main application class here
        # self.app = Application()
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Add basic tests here
        self.assertTrue(True, "Placeholder test - replace with actual tests")
    
    def test_error_handling(self):
        """Test error handling."""
        # Add error handling tests here
        self.assertTrue(True, "Placeholder test - replace with actual tests")
    
    def tearDown(self):
        """Clean up after tests."""
        pass

class TestFallbackGeneration(unittest.TestCase):
    """Test that fallback generation works."""
    
    def test_fallback_active(self):
        """Test that fallback test generation is working."""
        self.assertTrue(True, "Fallback test generation is active")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
'''
        
        return {
            'test_code': fallback_test_code,
            'additional_tests': [],
            'full_response': f"# Fallback Tests Generated\\n\\n```python\\n{fallback_test_code}\\n```",
            'fallback_used': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_deployment(self, code_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback deployment config when AI generation fails."""
        self.logger.info("Creating fallback deployment configuration")
        
        fallback_deployment = '''# Fallback Deployment Configuration

## Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./logs:/app/logs
```

## Basic Deployment Steps

1. **Prepare Environment**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**
   ```bash
   python main.py
   ```

3. **Docker Deployment**
   ```bash
   docker-compose up -d
   ```

## Environment Variables
- Set any required environment variables in your deployment environment
- Check the main application code for specific configuration needs

## Monitoring
- Check application logs for runtime information
- Monitor system resources as needed

**Note**: This is a fallback deployment configuration. Customize based on your specific requirements.
'''
        
        return {
            'deployment_configs': fallback_deployment,
            'fallback_used': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_ui_result(self, requirements: Dict[str, Any], code_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback UI result when AI generation fails."""
        self.logger.info("Creating fallback UI result")
        
        fallback_ui = self._create_fallback_ui(requirements, code_result.get('final_code', ''))
        
        return {
            'streamlit_app': fallback_ui,
            'additional_ui_files': [],
            'full_response': f"# Fallback UI Generated\\n\\n```python\\n{fallback_ui}\\n```",
            'generation_metadata': {
                'retry_count': 0,
                'generation_method': 'fallback',
                'code_blocks_found': 1,
                'response_length': len(fallback_ui)
            },
            'fallback_used': True,
            'timestamp': datetime.now().isoformat()
        }
