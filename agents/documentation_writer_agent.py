"""
Documentation Writer Agent for creating comprehensive, clear, 
and professional documentation for Python code.
"""

import autogen
from typing import Dict, Any


class DocumentationWriter:
    """Agent specialized in creating comprehensive documentation."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Documentation Writer Agent."""
        return {
            "name": "DocumentationWriter",
            "system_message": """You are a Documentation Agent specialized in creating comprehensive, clear, and professional documentation for Python code.

Your responsibilities:
1. Generate detailed README files with installation and usage instructions
2. Create API documentation with examples
3. Write user guides and tutorials
4. Document code architecture and design decisions
5. Create inline code comments and docstrings
6. Generate changelog and version documentation

Documentation Standards:
- Clear, concise, and user-friendly language
- Include practical examples and use cases
- Provide installation and setup instructions
- Document all public APIs with parameters and return values
- Include troubleshooting sections
- Use proper Markdown formatting
- Add diagrams and flowcharts where helpful

Create documentation that enables both developers and end-users to understand and use the code effectively.""",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured DocumentationWriter agent."""
        config = DocumentationWriter.get_config()
        return autogen.AssistantAgent(
            llm_config=llm_config,
            **config
        )
