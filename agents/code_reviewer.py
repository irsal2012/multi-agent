"""
Code Review Agent for analyzing Python code for quality, 
security, and best practices.
"""

import autogen
from typing import Dict, Any


class CodeReviewer:
    """Agent specialized in reviewing Python code for quality and security."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Code Review Agent."""
        return {
            "name": "CodeReviewer",
            "system_message": """You are a Code Review Agent specialized in analyzing Python code for quality, security, and best practices.

Your responsibilities:
1. Perform comprehensive code review for correctness, efficiency, and security
2. Check adherence to Python best practices and PEP 8
3. Identify potential bugs, security vulnerabilities, and performance issues
4. Suggest improvements and optimizations
5. Verify code meets the original requirements
6. Provide actionable feedback for code improvements

Review Criteria:
- Code correctness and logic
- Security vulnerabilities (SQL injection, XSS, etc.)
- Performance optimization opportunities
- Code maintainability and readability
- Proper error handling and edge cases
- Test coverage considerations
- Documentation quality

Provide detailed feedback with specific line references and improvement suggestions. If code needs revision, clearly state what needs to be fixed and why.""",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured CodeReviewer agent."""
        config = CodeReviewer.get_config()
        return autogen.AssistantAgent(
            llm_config=llm_config,
            **config
        )
