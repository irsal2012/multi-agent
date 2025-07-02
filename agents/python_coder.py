"""
Python Coding Agent for converting structured requirements 
into high-quality, functional Python code.
"""

import autogen
from typing import Dict, Any


class PythonCoder:
    """Agent specialized in generating high-quality Python code from requirements."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Python Coding Agent."""
        return {
            "name": "PythonCoder",
            "system_message": """You are a Python Coding Agent specialized in converting structured requirements into high-quality, functional Python code.

Your responsibilities:
1. Convert structured requirements into clean, maintainable Python code
2. Follow Python best practices (PEP 8, type hints, docstrings)
3. Implement proper error handling and logging
4. Create modular, reusable code with appropriate design patterns
5. Include comprehensive docstrings and comments
6. Ensure code is production-ready and follows SOLID principles

Code Standards:
- Use type hints for all function parameters and return values
- Include comprehensive docstrings (Google style)
- Implement proper exception handling
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Include logging where appropriate
- Create unit test-friendly code structure

Always provide complete, runnable code modules with proper imports and structure.""",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured PythonCoder agent."""
        config = PythonCoder.get_config()
        return autogen.AssistantAgent(
            llm_config=llm_config,
            **config
        )
