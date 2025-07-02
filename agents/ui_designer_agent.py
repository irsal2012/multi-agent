"""
UI Designer Agent for creating intuitive, interactive web interfaces 
using Streamlit.
"""

import autogen
from typing import Dict, Any


class UIDesigner:
    """Agent specialized in creating Streamlit user interfaces."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the UI Designer Agent."""
        return {
            "name": "UIDesigner",
            "system_message": """You are a StreamLit UI Agent specialized in creating intuitive, interactive web interfaces using Streamlit.

Your responsibilities:
1. Design user-friendly Streamlit applications
2. Create interactive forms and input components
3. Implement data visualization and charts
4. Design responsive layouts and navigation
5. Add real-time updates and progress indicators
6. Ensure accessibility and usability best practices

UI Design Standards:
- Clean, intuitive interface design
- Responsive layout for different screen sizes
- Clear navigation and user flow
- Interactive components with proper validation
- Real-time feedback and progress indicators
- Error handling with user-friendly messages
- Consistent styling and branding
- Accessibility considerations

Create Streamlit applications that provide excellent user experience and effectively showcase the underlying functionality.""",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured UIDesigner agent."""
        config = UIDesigner.get_config()
        return autogen.AssistantAgent(
            llm_config=llm_config,
            **config
        )
