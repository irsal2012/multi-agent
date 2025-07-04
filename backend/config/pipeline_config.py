"""
Configuration-driven pipeline system for flexible agent orchestration.
"""

import yaml
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class ExecutionMode(Enum):
    """Execution modes for pipeline steps."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

@dataclass
class PipelineStep:
    """Configuration for a single pipeline step."""
    agent_type: str
    config_type: str = "standard"
    depends_on: List[str] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    optional: bool = False
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    conditions: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate step configuration after initialization."""
        if isinstance(self.execution_mode, str):
            self.execution_mode = ExecutionMode(self.execution_mode)

@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""
    name: str
    description: str
    version: str = "1.0.0"
    steps: List[PipelineStep] = field(default_factory=list)
    global_timeout_seconds: Optional[int] = None
    max_parallel_steps: int = 3
    failure_strategy: str = "stop"  # "stop", "continue", "retry"
    metadata: Optional[Dict[str, Any]] = None
    
    def validate(self) -> List[str]:
        """Validate pipeline configuration and return any issues."""
        issues = []
        
        # Check for circular dependencies
        try:
            self._check_circular_dependencies()
        except ValueError as e:
            issues.append(str(e))
        
        # Validate step dependencies exist
        step_names = {step.agent_type for step in self.steps}
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_names:
                    issues.append(f"Step '{step.agent_type}' depends on unknown step '{dep}'")
        
        # Check for duplicate step names
        step_names_list = [step.agent_type for step in self.steps]
        duplicates = set([x for x in step_names_list if step_names_list.count(x) > 1])
        if duplicates:
            issues.append(f"Duplicate step names found: {duplicates}")
        
        return issues
    
    def _check_circular_dependencies(self):
        """Check for circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_name: str) -> bool:
            visited.add(step_name)
            rec_stack.add(step_name)
            
            # Find the step
            step = next((s for s in self.steps if s.agent_type == step_name), None)
            if not step:
                return False
            
            # Check all dependencies
            for dep in step.depends_on:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(step_name)
            return False
        
        for step in self.steps:
            if step.agent_type not in visited:
                if has_cycle(step.agent_type):
                    raise ValueError(f"Circular dependency detected involving '{step.agent_type}'")
    
    def get_execution_order(self) -> List[List[str]]:
        """
        Get steps in execution order, grouped by dependency level.
        Returns list of lists, where each inner list can be executed in parallel.
        """
        # Build dependency graph
        dependencies = {}
        for step in self.steps:
            dependencies[step.agent_type] = step.depends_on.copy()
        
        execution_order = []
        remaining_steps = set(dependencies.keys())
        
        while remaining_steps:
            # Find steps with no remaining dependencies
            ready_steps = []
            for step_name in remaining_steps:
                if not dependencies[step_name]:
                    ready_steps.append(step_name)
            
            if not ready_steps:
                raise ValueError("Cannot resolve dependencies - possible circular dependency")
            
            execution_order.append(ready_steps)
            
            # Remove completed steps from remaining and dependencies
            for completed_step in ready_steps:
                remaining_steps.remove(completed_step)
                for step_deps in dependencies.values():
                    if completed_step in step_deps:
                        step_deps.remove(completed_step)
        
        return execution_order
    
    def get_step(self, agent_type: str) -> Optional[PipelineStep]:
        """Get step configuration by agent type."""
        return next((step for step in self.steps if step.agent_type == agent_type), None)

class PipelineConfigManager:
    """Manager for loading and managing pipeline configurations."""
    
    def __init__(self, config_dir: str = "config/pipelines"):
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, PipelineConfig] = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load all pipeline configurations from the config directory."""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load YAML files
            yaml_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
            
            if not yaml_files:
                self.logger.info("No pipeline config files found, creating default configuration")
                self._create_default_config()
                return
            
            for yaml_file in yaml_files:
                try:
                    with open(yaml_file, 'r') as f:
                        data = yaml.safe_load(f)
                    
                    if 'pipelines' in data:
                        # Multiple pipelines in one file
                        for pipeline_name, pipeline_data in data['pipelines'].items():
                            self._load_pipeline_config(pipeline_name, pipeline_data)
                    else:
                        # Single pipeline in file
                        pipeline_name = yaml_file.stem
                        self._load_pipeline_config(pipeline_name, data)
                        
                except Exception as e:
                    self.logger.error(f"Failed to load config from {yaml_file}: {str(e)}")
            
            self.logger.info(f"Loaded {len(self._configs)} pipeline configurations")
            
        except Exception as e:
            self.logger.error(f"Failed to load pipeline configurations: {str(e)}")
            self._create_default_config()
    
    def _load_pipeline_config(self, name: str, data: Dict[str, Any]):
        """Load a single pipeline configuration from data."""
        try:
            # Parse steps
            steps = []
            for step_data in data.get('steps', []):
                step = PipelineStep(
                    agent_type=step_data['agent_type'],
                    config_type=step_data.get('config_type', 'standard'),
                    depends_on=step_data.get('depends_on', []),
                    execution_mode=ExecutionMode(step_data.get('execution_mode', 'sequential')),
                    optional=step_data.get('optional', False),
                    timeout_seconds=step_data.get('timeout_seconds'),
                    retry_count=step_data.get('retry_count', 0),
                    conditions=step_data.get('conditions'),
                    parameters=step_data.get('parameters')
                )
                steps.append(step)
            
            # Create pipeline config
            pipeline_config = PipelineConfig(
                name=name,
                description=data.get('description', ''),
                version=data.get('version', '1.0.0'),
                steps=steps,
                global_timeout_seconds=data.get('global_timeout_seconds'),
                max_parallel_steps=data.get('max_parallel_steps', 3),
                failure_strategy=data.get('failure_strategy', 'stop'),
                metadata=data.get('metadata')
            )
            
            # Validate configuration
            issues = pipeline_config.validate()
            if issues:
                self.logger.warning(f"Pipeline '{name}' has validation issues: {issues}")
            
            self._configs[name] = pipeline_config
            
        except Exception as e:
            self.logger.error(f"Failed to parse pipeline config '{name}': {str(e)}")
    
    def _create_default_config(self):
        """Create default pipeline configuration."""
        default_config = PipelineConfig(
            name="default",
            description="Standard multi-agent development pipeline",
            steps=[
                PipelineStep(
                    agent_type="requirement_analyst",
                    config_type="standard"
                ),
                PipelineStep(
                    agent_type="python_coder",
                    config_type="coding",
                    depends_on=["requirement_analyst"]
                ),
                PipelineStep(
                    agent_type="code_reviewer",
                    config_type="review",
                    depends_on=["python_coder"]
                ),
                PipelineStep(
                    agent_type="test_generator",
                    config_type="coding",
                    depends_on=["python_coder"],
                    execution_mode=ExecutionMode.PARALLEL
                ),
                PipelineStep(
                    agent_type="documentation_writer",
                    config_type="creative",
                    depends_on=["code_reviewer"],
                    execution_mode=ExecutionMode.PARALLEL
                ),
                PipelineStep(
                    agent_type="deployment_engineer",
                    config_type="standard",
                    depends_on=["test_generator"]
                ),
                PipelineStep(
                    agent_type="ui_designer",
                    config_type="creative",
                    depends_on=["documentation_writer"]
                )
            ]
        )
        
        self._configs["default"] = default_config
        
        # Save default config to file
        self._save_config_to_file("default", default_config)
    
    def _save_config_to_file(self, name: str, config: PipelineConfig):
        """Save a pipeline configuration to file."""
        try:
            config_file = self.config_dir / f"{name}.yaml"
            
            # Convert to dict for YAML serialization
            config_dict = {
                "name": config.name,
                "description": config.description,
                "version": config.version,
                "global_timeout_seconds": config.global_timeout_seconds,
                "max_parallel_steps": config.max_parallel_steps,
                "failure_strategy": config.failure_strategy,
                "metadata": config.metadata,
                "steps": []
            }
            
            for step in config.steps:
                step_dict = {
                    "agent_type": step.agent_type,
                    "config_type": step.config_type,
                    "execution_mode": step.execution_mode.value,
                    "optional": step.optional
                }
                
                if step.depends_on:
                    step_dict["depends_on"] = step.depends_on
                if step.timeout_seconds:
                    step_dict["timeout_seconds"] = step.timeout_seconds
                if step.retry_count > 0:
                    step_dict["retry_count"] = step.retry_count
                if step.conditions:
                    step_dict["conditions"] = step.conditions
                if step.parameters:
                    step_dict["parameters"] = step.parameters
                
                config_dict["steps"].append(step_dict)
            
            with open(config_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved pipeline config '{name}' to {config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config '{name}': {str(e)}")
    
    def get_pipeline_config(self, name: str = "default") -> PipelineConfig:
        """Get pipeline configuration by name."""
        if name not in self._configs:
            self.logger.warning(f"Pipeline '{name}' not found, using default")
            name = "default"
        
        return self._configs.get(name, self._configs["default"])
    
    def get_available_pipelines(self) -> List[str]:
        """Get list of available pipeline names."""
        return list(self._configs.keys())
    
    def add_pipeline_config(self, config: PipelineConfig, save_to_file: bool = True) -> bool:
        """Add a new pipeline configuration."""
        try:
            # Validate configuration
            issues = config.validate()
            if issues:
                self.logger.error(f"Cannot add invalid pipeline '{config.name}': {issues}")
                return False
            
            self._configs[config.name] = config
            
            if save_to_file:
                self._save_config_to_file(config.name, config)
            
            self.logger.info(f"Added pipeline configuration '{config.name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add pipeline config '{config.name}': {str(e)}")
            return False
    
    def reload_configs(self):
        """Reload all configurations from disk."""
        self._configs.clear()
        self._load_configs()

# Global pipeline config manager
pipeline_config_manager = PipelineConfigManager()
