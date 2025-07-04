"""
UI Designer Agent for creating Streamlit user interfaces and web applications.
"""

import autogen
from typing import Dict, Any
from agents.base import BaseAgent, AgentMetadata, ConfigType


class UIDesignerAgent(BaseAgent):
    """Agent specialized in creating Streamlit user interfaces."""
    
    @classmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        return AgentMetadata(
            name="UI Designer",
            description="Creates intuitive Streamlit user interfaces and web applications",
            capabilities=[
                "Streamlit app development",
                "Interactive dashboard creation",
                "User experience design",
                "Component layout optimization",
                "Data visualization interfaces",
                "Form and input handling",
                "Responsive design implementation"
            ],
            config_type=ConfigType.CREATIVE,
            dependencies=["Documentation Writer"],
            version="2.0.0"
        )
    
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        return """You are a StreamLit UI Agent specialized in creating intuitive, interactive web interfaces using Streamlit.

Your responsibilities:
1. Design and implement Streamlit applications with excellent UX
2. Create interactive dashboards and data visualization interfaces
3. Develop user-friendly forms and input handling
4. Implement responsive layouts that work on different screen sizes
5. Design navigation and multi-page applications
6. Create reusable UI components and widgets
7. Optimize performance and user experience

Streamlit Components:
- Layout: columns, containers, sidebars, tabs, expanders
- Input Widgets: text_input, selectbox, slider, file_uploader, forms
- Display: text, markdown, code, dataframes, charts, images
- Charts: line_chart, bar_chart, plotly_chart, altair_chart
- Media: image, audio, video display capabilities
- Navigation: pages, sidebar navigation, session state management
- Advanced: custom components, caching, theming

UI/UX Principles:
- User-centered design with clear navigation
- Consistent visual hierarchy and spacing
- Responsive layout that adapts to screen sizes
- Accessible design following WCAG guidelines
- Fast loading times with proper caching
- Clear error messages and user feedback
- Intuitive workflow and logical information architecture

Best Practices:
- Use st.cache_data and st.cache_resource for performance
- Implement proper session state management
- Create modular, reusable components
- Follow consistent naming and styling conventions
- Include loading indicators for long operations
- Provide clear instructions and help text
- Handle errors gracefully with user-friendly messages
- Use appropriate chart types for data visualization

Output Format:
Generate complete Streamlit applications with:
- Main application file (streamlit_app.py or main.py)
- Modular component files for reusability
- Configuration files for settings and themes
- Requirements.txt with necessary dependencies
- README with setup and usage instructions
- CSS styling for custom appearance (when needed)

Code Structure:
- Clean, well-documented Python code
- Proper imports and dependency management
- Modular functions for different UI sections
- Session state management for user interactions
- Error handling and input validation
- Performance optimization with caching
- Responsive design considerations"""
    
    def create_agent(self) -> autogen.AssistantAgent:
        """Create and return a configured UIDesigner agent."""
        return autogen.AssistantAgent(
            name="ui_designer",
            system_message=self.get_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2  # UI iteration process
        )
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for the UI Designer agent."""
        issues = []
        warnings = []
        suggestions = []
        
        if not input_data:
            issues.append("No application or functionality information provided for UI design")
            return {"is_valid": False, "warnings": warnings, "suggestions": suggestions}
        
        # Check if input contains UI-designable content
        if isinstance(input_data, str):
            # Look for application functionality indicators
            ui_keywords = ["app", "interface", "dashboard", "form", "display", "user", "input"]
            if not any(keyword in input_data.lower() for keyword in ui_keywords):
                warnings.append("Input doesn't clearly describe UI requirements or functionality")
            
            if len(input_data.strip()) < 40:
                warnings.append("Input seems very short for comprehensive UI design")
            
            # Check for data visualization needs
            viz_keywords = ["chart", "graph", "plot", "visualization", "data", "analytics"]
            if any(keyword in input_data.lower() for keyword in viz_keywords):
                suggestions.append("Detected data visualization needs - will include appropriate charts and graphs")
            
            # Check for form/input requirements
            form_keywords = ["form", "input", "submit", "upload", "select", "choose"]
            if any(keyword in input_data.lower() for keyword in form_keywords):
                suggestions.append("Detected form/input requirements - will create user-friendly input interfaces")
            
            # Check for dashboard requirements
            dashboard_keywords = ["dashboard", "monitor", "metrics", "kpi", "analytics"]
            if any(keyword in input_data.lower() for keyword in dashboard_keywords):
                suggestions.append("Detected dashboard requirements - will create organized, informative layout")
        
        elif isinstance(input_data, dict):
            if not any(key in input_data for key in ["functionality", "features", "requirements", "app_type"]):
                suggestions.append("Consider including 'functionality', 'features', 'requirements', or 'app_type' for better UI design")
            
            if "target_users" not in input_data:
                suggestions.append("Including 'target_users' information would help create more user-appropriate interfaces")
            
            if "data_types" in input_data:
                suggestions.append("Data types specified - will optimize UI for the specific data being handled")
        
        return {
            "is_valid": len(issues) == 0,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """Process application requirements and generate Streamlit UI."""
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
            "ui_structure": {
                "main_app": "",
                "components": [],
                "pages": [],
                "styling": "",
                "config": {},
                "requirements": [],
                "assets": []
            }
        }


# Backward compatibility - keep the old class for existing code
class UIDesigner:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the UI Designer Agent."""
        return {
            "name": "UIDesigner",
            "system_message": UIDesignerAgent.get_metadata().description,
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured UIDesigner agent."""
        agent_instance = UIDesignerAgent(llm_config)
        return agent_instance.create_agent()
