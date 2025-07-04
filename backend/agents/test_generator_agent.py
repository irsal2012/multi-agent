"""
Test Generator Agent for creating comprehensive test cases for Python code.
"""

import autogen
from typing import Dict, Any
from agents.base import BaseAgent, AgentMetadata, ConfigType


class TestGeneratorAgent(BaseAgent):
    """Agent specialized in generating comprehensive test cases."""
    
    @classmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        return AgentMetadata(
            name="Test Generator",
            description="Creates comprehensive test suites for Python code",
            capabilities=[
                "Unit test generation",
                "Integration test creation",
                "Test coverage analysis",
                "Edge case testing",
                "Mock object creation",
                "Test data generation",
                "Performance testing"
            ],
            config_type=ConfigType.CODING,
            dependencies=["Python Coder"],
            version="2.0.0"
        )
    
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        return """You are a Test Case Generation Agent specialized in creating comprehensive test suites for Python code.

Your responsibilities:
1. Generate unit tests for all functions and methods
2. Create integration tests for component interactions
3. Design edge case and boundary condition tests
4. Implement mock objects for external dependencies
5. Generate test data and fixtures
6. Create performance and load tests when appropriate
7. Ensure high test coverage and quality

Test Types to Generate:
- Unit Tests: Individual function/method testing
- Integration Tests: Component interaction testing
- Edge Case Tests: Boundary conditions and error scenarios
- Performance Tests: Speed and resource usage validation
- Security Tests: Input validation and vulnerability testing
- Regression Tests: Prevent future bugs
- End-to-End Tests: Complete workflow validation

Testing Frameworks:
- Use pytest as the primary testing framework
- Include unittest for compatibility when needed
- Use mock/unittest.mock for mocking dependencies
- Include fixtures for test data setup
- Use parametrized tests for multiple scenarios

Output Format:
Generate complete test files with:
- Proper imports and setup
- Test classes organized by functionality
- Individual test methods with descriptive names
- Test fixtures and mock objects
- Assertions that validate expected behavior
- Error case testing with appropriate exceptions
- Performance benchmarks where relevant

Standards:
- Follow pytest conventions and best practices
- Use descriptive test method names (test_should_do_something_when_condition)
- Include docstrings explaining test purpose
- Test both positive and negative scenarios
- Aim for high code coverage (>90%)
- Include setup and teardown methods when needed
- Use appropriate assertion methods
- Mock external dependencies properly"""
    
    def create_agent(self) -> autogen.AssistantAgent:
        """Create and return a configured TestGenerator agent."""
        return autogen.AssistantAgent(
            name="test_generator",
            system_message=self.get_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2  # Test generation process
        )
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for the Test Generator agent."""
        issues = []
        warnings = []
        suggestions = []
        
        if not input_data:
            issues.append("No code provided for test generation")
            return {"is_valid": False, "warnings": warnings, "suggestions": suggestions}
        
        # Check if input contains code to test
        if isinstance(input_data, str):
            # Look for testable Python code
            testable_keywords = ["def ", "class ", "async def"]
            if not any(keyword in input_data for keyword in testable_keywords):
                warnings.append("Input doesn't appear to contain testable Python functions or classes")
            
            if len(input_data.strip()) < 30:
                warnings.append("Code seems very short for meaningful test generation")
            
            # Check for existing tests
            if "test_" in input_data.lower() or "assert" in input_data.lower():
                suggestions.append("Input appears to already contain tests - consider separating source code from tests")
            
            # Check for complex logic that needs testing
            complex_keywords = ["if ", "for ", "while ", "try:", "except"]
            if any(keyword in input_data for keyword in complex_keywords):
                suggestions.append("Code contains control flow - ensure edge cases are thoroughly tested")
        
        elif isinstance(input_data, dict):
            if "code" not in input_data and "source" not in input_data and "functions" not in input_data:
                suggestions.append("Consider including 'code', 'source', or 'functions' key in input data")
        
        return {
            "is_valid": len(issues) == 0,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """Process code and generate comprehensive tests."""
        # Validate input first
        validation = self.validate_input(input_data)
        if not validation["is_valid"]:
            return {
                "error": "Invalid input data",
                "validation_issues": validation
            }
        
        # Get the agent instance
        agent = self.get_agent()
        
        # Process the input (this would typically involve AutoGen conversation)
        # For now, return a structured response
        return {
            "agent": self.metadata.name,
            "input_processed": True,
            "validation": validation,
            "context": context,
            "agent_instance": agent.name if agent else None,
            "test_structure": {
                "unit_tests": [],
                "integration_tests": [],
                "edge_case_tests": [],
                "performance_tests": [],
                "mock_objects": [],
                "test_fixtures": [],
                "test_coverage_target": 90
            }
        }


# Backward compatibility - keep the old class for existing code
class TestGenerator:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Test Generator Agent."""
        return {
            "name": "TestGenerator",
            "system_message": TestGeneratorAgent.get_metadata().description,
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured TestGenerator agent."""
        agent_instance = TestGeneratorAgent(llm_config)
        return agent_instance.create_agent()
