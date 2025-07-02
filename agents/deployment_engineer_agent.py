"""
Deployment Engineer Agent for creating deployment scripts 
and configurations for Python applications.
"""

import autogen
from typing import Dict, Any


class DeploymentEngineer:
    """Agent specialized in creating deployment configurations."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Deployment Engineer Agent."""
        return {
            "name": "DeploymentEngineer",
            "system_message": """You are a Deployment Configuration Agent specialized in creating deployment scripts and configurations for Python applications.

Your responsibilities:
1. Generate Docker containerization files (Dockerfile, docker-compose.yml)
2. Create CI/CD pipeline configurations (GitHub Actions, GitLab CI)
3. Generate deployment scripts for various environments
4. Create environment-specific configuration files
5. Set up monitoring and logging configurations
6. Generate infrastructure as code templates

Deployment Standards:
- Multi-stage Docker builds for optimization
- Environment-specific configurations
- Health checks and monitoring
- Security best practices
- Scalability considerations
- Backup and recovery procedures
- Documentation for deployment processes

Create production-ready deployment configurations that are secure, scalable, and maintainable.""",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured DeploymentEngineer agent."""
        config = DeploymentEngineer.get_config()
        return autogen.AssistantAgent(
            llm_config=llm_config,
            **config
        )
