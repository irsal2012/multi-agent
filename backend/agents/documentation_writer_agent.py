"""
Documentation Writer Agent for creating comprehensive documentation for Python projects.
"""

import autogen
from typing import Dict, Any
from agents.base import BaseAgent, AgentMetadata, ConfigType


class DocumentationWriterAgent(BaseAgent):
    """Agent specialized in creating comprehensive documentation."""
    
    @classmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        return AgentMetadata(
            name="Documentation Writer",
            description="Creates comprehensive documentation for Python projects",
            capabilities=[
                "API documentation generation",
                "User guide creation",
                "Technical specification writing",
                "README file generation",
                "Code comment enhancement",
                "Tutorial creation",
                "Architecture documentation"
            ],
            config_type=ConfigType.CREATIVE,
            dependencies=["Code Reviewer"],
            version="2.0.0"
        )
    
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        return """You are a Documentation Agent specialized in creating comprehensive, clear, and professional documentation for Python code and projects.

Your responsibilities:
1. Generate API documentation from code and docstrings
2. Create user-friendly README files with setup instructions
3. Write technical specifications and architecture documentation
4. Develop tutorials and usage examples
5. Enhance code comments and docstrings
6. Create installation and deployment guides
7. Generate changelog and release notes

Documentation Types:
- API Documentation: Function/class references with examples
- User Guides: Step-by-step instructions for end users
- Developer Guides: Technical documentation for contributors
- README Files: Project overview, setup, and quick start
- Architecture Docs: System design and component relationships
- Tutorials: Learning-oriented documentation with examples
- Reference Docs: Comprehensive technical specifications

Documentation Standards:
- Use clear, concise language appropriate for the audience
- Include practical examples and code snippets
- Follow markdown formatting conventions
- Structure content with proper headings and navigation
- Include installation, usage, and troubleshooting sections
- Provide links to related resources and dependencies
- Use consistent terminology throughout

Output Format:
Generate well-structured documentation with:
- Clear headings and table of contents
- Code examples with syntax highlighting
- Installation and setup instructions
- Usage examples and tutorials
- API reference with parameters and return values
- Troubleshooting and FAQ sections
- Contributing guidelines when appropriate

Writing Style:
- Write for your target audience (users vs developers)
- Use active voice and present tense
- Be specific and avoid ambiguous language
- Include prerequisites and assumptions
- Provide context and explain the "why" not just "how"
- Use bullet points and numbered lists for clarity
- Include visual aids (diagrams, screenshots) when helpful"""
    
    def create_agent(self) -> autogen.AssistantAgent:
        """Create and return a configured DocumentationWriter agent."""
        return autogen.AssistantAgent(
            name="documentation_writer",
            system_message=self.get_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2  # Documentation creation process
        )
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for the Documentation Writer agent."""
        issues = []
        warnings = []
        suggestions = []
        
        if not input_data:
            issues.append("No code or project information provided for documentation")
            return {"is_valid": False, "warnings": warnings, "suggestions": suggestions}
        
        # Check if input contains documentable content
        if isinstance(input_data, str):
            # Look for code that needs documentation
            doc_keywords = ["def ", "class ", "import ", "from "]
            if not any(keyword in input_data for keyword in doc_keywords):
                warnings.append("Input doesn't appear to contain Python code that needs documentation")
            
            if len(input_data.strip()) < 50:
                warnings.append("Input seems very short for comprehensive documentation")
            
            # Check for existing documentation
            if "\"\"\"" in input_data or "'''" in input_data:
                suggestions.append("Code already contains docstrings - consider enhancing or standardizing them")
            
            # Check for complex functionality
            complex_indicators = ["class ", "def ", "async ", "import"]
            complexity_count = sum(1 for indicator in complex_indicators if indicator in input_data)
            if complexity_count > 5:
                suggestions.append("Code appears complex - consider creating both API docs and user guides")
        
        elif isinstance(input_data, dict):
            if not any(key in input_data for key in ["code", "project", "functions", "classes"]):
                suggestions.append("Consider including 'code', 'project', 'functions', or 'classes' key in input data")
            
            if "project_name" not in input_data:
                suggestions.append("Including 'project_name' would help create better documentation")
        
        return {
            "is_valid": len(issues) == 0,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """Process code/project and generate comprehensive documentation."""
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
            "documentation_structure": {
                "readme": "",
                "api_docs": [],
                "user_guide": "",
                "developer_guide": "",
                "installation_guide": "",
                "tutorials": [],
                "changelog": "",
                "contributing_guide": ""
            }
        }


# Backward compatibility - keep the old class for existing code
class DocumentationWriter:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Documentation Writer Agent."""
        return {
            "name": "DocumentationWriter",
            "system_message": DocumentationWriterAgent.get_metadata().description,
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured DocumentationWriter agent."""
        agent_instance = DocumentationWriterAgent(llm_config)
        return agent_instance.create_agent()
