"""
Model configuration for the Multi-Agent Framework.
Handles OpenAI and other LLM configurations.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class ModelConfig:
    """Configuration class for LLM models."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL")
        self.openai_organization = os.getenv("OPENAI_ORGANIZATION")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get the LLM configuration for AutoGen agents."""
        config = {
            "config_list": [
                {
                    "model": self.openai_model,
                    "api_key": self.openai_api_key,
                }
            ],
            "timeout": 120,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if self.openai_base_url:
            config["config_list"][0]["base_url"] = self.openai_base_url
        
        if self.openai_organization:
            config["config_list"][0]["organization"] = self.openai_organization
            
        return config
    
    def get_coding_config(self) -> Dict[str, Any]:
        """Get specialized config for coding tasks."""
        config = self.get_llm_config()
        config["temperature"] = 0.1  # Lower temperature for code
        return config
    
    def get_review_config(self) -> Dict[str, Any]:
        """Get specialized config for code review tasks."""
        config = self.get_llm_config()
        config["temperature"] = 0.2  # Low temperature for analysis
        return config
    
    def get_creative_config(self) -> Dict[str, Any]:
        """Get specialized config for creative tasks like documentation."""
        config = self.get_llm_config()
        config["temperature"] = 0.8  # Higher temperature for creativity
        return config

# Global model configuration instance
model_config = ModelConfig()
