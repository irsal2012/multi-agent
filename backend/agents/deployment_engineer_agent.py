"""
Deployment Engineer Agent for creating deployment configurations and infrastructure setup.
"""

import autogen
from typing import Dict, Any
from agents.base import BaseAgent, AgentMetadata, ConfigType


class DeploymentEngineerAgent(BaseAgent):
    """Agent specialized in creating deployment configurations."""
    
    @classmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        return AgentMetadata(
            name="Deployment Engineer",
            description="Creates deployment configurations and infrastructure setup for Python applications",
            capabilities=[
                "Docker containerization",
                "CI/CD pipeline creation",
                "Cloud deployment configuration",
                "Environment setup scripts",
                "Infrastructure as Code",
                "Monitoring and logging setup",
                "Security configuration"
            ],
            config_type=ConfigType.STANDARD,
            dependencies=["Test Generator"],
            version="2.0.0"
        )
    
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        return """You are a Deployment Configuration Agent specialized in creating deployment scripts and configurations for Python applications.

Your responsibilities:
1. Create Docker containers and docker-compose configurations
2. Design CI/CD pipelines for automated deployment
3. Generate cloud deployment configurations (AWS, GCP, Azure)
4. Create environment setup and configuration scripts
5. Implement Infrastructure as Code (Terraform, CloudFormation)
6. Set up monitoring, logging, and alerting
7. Configure security and access controls

Deployment Targets:
- Containerization: Docker, Kubernetes, container orchestration
- Cloud Platforms: AWS, Google Cloud, Azure, DigitalOcean
- CI/CD: GitHub Actions, GitLab CI, Jenkins, CircleCI
- Infrastructure: Terraform, CloudFormation, Ansible
- Monitoring: Prometheus, Grafana, ELK stack, CloudWatch
- Security: SSL/TLS, secrets management, access controls

Configuration Types:
- Dockerfile: Multi-stage builds, optimization, security
- docker-compose.yml: Service orchestration, networking, volumes
- CI/CD Pipelines: Build, test, deploy automation
- Environment Files: Configuration management, secrets
- Infrastructure Scripts: Resource provisioning, scaling
- Monitoring Configs: Metrics, logs, alerts, dashboards

Best Practices:
- Use multi-stage Docker builds for optimization
- Implement proper secret management
- Follow security best practices (non-root users, minimal images)
- Include health checks and readiness probes
- Set up proper logging and monitoring
- Use environment-specific configurations
- Implement blue-green or rolling deployments
- Include backup and disaster recovery plans

Output Format:
Generate complete deployment configurations:
- Dockerfile with optimized layers and security
- docker-compose.yml for local development and testing
- CI/CD pipeline files with proper stages
- Environment configuration files
- Infrastructure as Code templates
- Monitoring and alerting configurations
- Deployment scripts and documentation

Standards:
- Follow container and cloud best practices
- Use official base images and keep them updated
- Implement proper resource limits and requests
- Include comprehensive health checks
- Set up structured logging and metrics
- Use secrets management for sensitive data
- Document deployment procedures and troubleshooting"""
    
    def create_agent(self) -> autogen.AssistantAgent:
        """Create and return a configured DeploymentEngineer agent."""
        return autogen.AssistantAgent(
            name="deployment_engineer",
            system_message=self.get_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1  # Configuration generation
        )
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for the Deployment Engineer agent."""
        issues = []
        warnings = []
        suggestions = []
        
        if not input_data:
            issues.append("No application information provided for deployment configuration")
            return {"is_valid": False, "warnings": warnings, "suggestions": suggestions}
        
        # Check if input contains deployable application info
        if isinstance(input_data, str):
            # Look for application indicators
            app_keywords = ["app", "main", "server", "api", "web", "service"]
            if not any(keyword in input_data.lower() for keyword in app_keywords):
                warnings.append("Input doesn't clearly indicate what type of application to deploy")
            
            if len(input_data.strip()) < 30:
                warnings.append("Input seems very short for comprehensive deployment configuration")
            
            # Check for framework indicators
            frameworks = ["flask", "django", "fastapi", "streamlit", "tornado"]
            detected_frameworks = [fw for fw in frameworks if fw in input_data.lower()]
            if detected_frameworks:
                suggestions.append(f"Detected {', '.join(detected_frameworks)} - will optimize deployment for these frameworks")
            
            # Check for database requirements
            databases = ["postgres", "mysql", "mongodb", "redis", "sqlite"]
            detected_dbs = [db for db in databases if db in input_data.lower()]
            if detected_dbs:
                suggestions.append(f"Detected database requirements: {', '.join(detected_dbs)} - will include in deployment config")
        
        elif isinstance(input_data, dict):
            required_keys = ["application_type", "framework", "dependencies"]
            missing_keys = [key for key in required_keys if key not in input_data]
            if missing_keys:
                suggestions.append(f"Consider including these keys for better deployment config: {', '.join(missing_keys)}")
            
            if "target_platform" not in input_data:
                suggestions.append("Specify 'target_platform' (docker, aws, gcp, azure) for optimized deployment")
        
        return {
            "is_valid": len(issues) == 0,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """Process application info and generate deployment configurations."""
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
            "deployment_structure": {
                "dockerfile": "",
                "docker_compose": "",
                "ci_cd_pipeline": "",
                "environment_configs": {},
                "infrastructure_code": "",
                "monitoring_config": "",
                "deployment_scripts": [],
                "security_configs": {}
            }
        }


# Backward compatibility - keep the old class for existing code
class DeploymentEngineer:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Deployment Engineer Agent."""
        return {
            "name": "DeploymentEngineer",
            "system_message": DeploymentEngineerAgent.get_metadata().description,
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 1,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured DeploymentEngineer agent."""
        agent_instance = DeploymentEngineerAgent(llm_config)
        return agent_instance.create_agent()
