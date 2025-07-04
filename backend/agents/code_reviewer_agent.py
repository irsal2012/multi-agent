"""
Code Review Agent for analyzing Python code quality, security, and best practices.
"""

import autogen
from typing import Dict, Any
from agents.base import BaseAgent, AgentMetadata, ConfigType


class CodeReviewerAgent(BaseAgent):
    """Agent specialized in reviewing Python code for quality and security."""
    
    @classmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        return AgentMetadata(
            name="Code Reviewer",
            description="Reviews Python code for quality, security, and best practices",
            capabilities=[
                "Code quality analysis",
                "Security vulnerability detection",
                "Performance optimization suggestions",
                "Best practices enforcement",
                "Code style compliance",
                "Architecture review",
                "Refactoring recommendations"
            ],
            config_type=ConfigType.REVIEW,
            dependencies=["Python Coder"],
            version="2.0.0"
        )
    
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        return """You are a Code Review Agent specialized in analyzing Python code for quality, security, and best practices.

Your responsibilities:
1. Review Python code for quality, readability, and maintainability
2. Identify security vulnerabilities and potential exploits
3. Suggest performance optimizations and improvements
4. Ensure adherence to Python best practices (PEP 8, SOLID principles)
5. Check for proper error handling and logging
6. Validate code architecture and design patterns
7. Recommend refactoring opportunities

Review Areas:
- Code Quality: Readability, maintainability, complexity
- Security: Input validation, SQL injection, XSS, authentication
- Performance: Algorithm efficiency, memory usage, bottlenecks
- Best Practices: PEP 8, type hints, docstrings, naming conventions
- Architecture: SOLID principles, design patterns, modularity
- Testing: Testability, test coverage considerations
- Documentation: Code comments, docstrings, API documentation

Output Format:
Provide structured feedback in JSON format:
- overall_score: 1-10 rating
- critical_issues: Security vulnerabilities, major bugs
- major_issues: Performance problems, architecture concerns
- minor_issues: Style violations, minor improvements
- suggestions: Specific improvement recommendations
- security_concerns: Detailed security analysis
- performance_notes: Performance optimization opportunities
- best_practices: Adherence to Python standards
- refactoring_opportunities: Code improvement suggestions

Standards:
- Be constructive and specific in feedback
- Prioritize security and critical issues first
- Provide actionable suggestions with examples
- Consider maintainability and scalability
- Reference specific lines or functions when possible"""
    
    def create_agent(self) -> autogen.AssistantAgent:
        """Create and return a configured CodeReviewer agent."""
        return autogen.AssistantAgent(
            name="code_reviewer",
            system_message=self.get_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2  # Focused review process
        )
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for the Code Reviewer agent."""
        issues = []
        warnings = []
        suggestions = []
        
        if not input_data:
            issues.append("No code provided for review")
            return {"is_valid": False, "warnings": warnings, "suggestions": suggestions}
        
        # Check if input contains code
        if isinstance(input_data, str):
            # Look for Python code indicators
            python_keywords = ["def ", "class ", "import ", "from ", "if __name__"]
            if not any(keyword in input_data for keyword in python_keywords):
                warnings.append("Input doesn't appear to contain Python code")
            
            if len(input_data.strip()) < 50:
                warnings.append("Code seems very short for meaningful review")
            
            # Check for common code smells
            code_smells = ["TODO", "FIXME", "HACK", "XXX"]
            if any(smell in input_data.upper() for smell in code_smells):
                suggestions.append("Code contains TODO/FIXME comments that should be addressed")
        
        elif isinstance(input_data, dict):
            if "code" not in input_data and "source" not in input_data:
                suggestions.append("Consider including 'code' or 'source' key in input data")
        
        return {
            "is_valid": len(issues) == 0,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """Process code and generate review feedback."""
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
            "review_structure": {
                "overall_score": 0,
                "critical_issues": [],
                "major_issues": [],
                "minor_issues": [],
                "suggestions": [],
                "security_concerns": [],
                "performance_notes": [],
                "best_practices": [],
                "refactoring_opportunities": []
            }
        }


# Backward compatibility - keep the old class for existing code
class CodeReviewer:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Code Review Agent."""
        return {
            "name": "CodeReviewer",
            "system_message": CodeReviewerAgent.get_metadata().description,
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured CodeReviewer agent."""
        agent_instance = CodeReviewerAgent(llm_config)
        return agent_instance.create_agent()
