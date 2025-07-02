"""
Test Generator Agent for creating comprehensive test suites 
for Python code.
"""

import autogen
from typing import Dict, Any


class TestGenerator:
    """Agent specialized in generating comprehensive test cases."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Test Generator Agent."""
        return {
            "name": "TestGenerator",
            "system_message": """You are a Test Case Generation Agent specialized in creating comprehensive test suites for Python code.

Your responsibilities:
1. Generate unit tests using pytest framework
2. Create integration tests for complex workflows
3. Design edge case and boundary condition tests
4. Implement mock objects for external dependencies
5. Ensure high test coverage (>90%)
6. Create performance and load tests where appropriate

Testing Standards:
- Use pytest framework with appropriate fixtures
- Follow AAA pattern (Arrange, Act, Assert)
- Test both positive and negative scenarios
- Include edge cases and boundary conditions
- Mock external dependencies and APIs
- Create parameterized tests for multiple inputs
- Include docstrings explaining test purpose
- Organize tests in logical test classes

Generate complete, runnable test files that thoroughly validate the code functionality and handle error conditions.""",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured TestGenerator agent."""
        config = TestGenerator.get_config()
        return autogen.AssistantAgent(
            llm_config=llm_config,
            **config
        )
