"""
Python Coding Agent for converting structured requirements 
into high-quality, functional Python code.
"""

import autogen
from typing import Dict, Any
from agents.base import BaseAgent, AgentMetadata, ConfigType


class PythonCoderAgent(BaseAgent):
    """Agent specialized in generating high-quality Python code from requirements."""
    
    @classmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        return AgentMetadata(
            name="Python Coder",
            description="Generates high-quality Python code from structured requirements",
            capabilities=[
                "Python code generation",
                "Best practices implementation",
                "Type hints and documentation",
                "Error handling and logging",
                "SOLID principles adherence",
                "PEP 8 compliance",
                "Modular code design"
            ],
            config_type=ConfigType.CODING,
            dependencies=["Requirement Analyst"],
            version="2.0.0"
        )
    
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        return """You are a Python Coding Agent specialized in converting structured requirements into high-quality, functional Python code.

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

Always provide complete, runnable code modules with proper imports and structure."""
    
    def create_agent(self) -> autogen.AssistantAgent:
        """Create and return a configured PythonCoder agent."""
        return autogen.AssistantAgent(
            name="python_coder",
            system_message=self.get_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2
        )
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for the Python Coder agent."""
        issues = []
        warnings = []
        suggestions = []
        
        if not input_data:
            issues.append("No input data provided")
            return {"is_valid": False, "warnings": warnings, "suggestions": suggestions}
        
        # Check if input contains requirements
        if isinstance(input_data, str):
            if len(input_data.strip()) < 10:
                warnings.append("Input seems very short for meaningful code generation")
            
            if "requirement" not in input_data.lower() and "function" not in input_data.lower():
                suggestions.append("Consider providing more structured requirements or function specifications")
        
        elif isinstance(input_data, dict):
            if "requirements" not in input_data and "specifications" not in input_data:
                suggestions.append("Consider including 'requirements' or 'specifications' key in input data")
        
        return {
            "is_valid": len(issues) == 0,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """Process requirements and generate Python code."""
        # Validate input first
        validation = self.validate_input(input_data)
        if not validation["is_valid"]:
            return {
                "error": "Invalid input data",
                "validation_issues": validation
            }
        
        # Extract requirements from input
        if isinstance(input_data, str):
            requirements = input_data
        elif isinstance(input_data, dict):
            requirements = input_data.get('requirements', input_data.get('user_input', str(input_data)))
        else:
            requirements = str(input_data)
        
        # Generate actual Python code based on requirements
        try:
            generated_code = self._generate_code_from_requirements(requirements)
            
            return {
                "agent": self.metadata.name,
                "success": True,
                "generated_code": generated_code,
                "requirements": requirements,
                "validation": validation,
                "context": context,
                "files_created": list(generated_code.keys()) if isinstance(generated_code, dict) else ["main.py"]
            }
            
        except Exception as e:
            return {
                "agent": self.metadata.name,
                "success": False,
                "error": str(e),
                "requirements": requirements,
                "validation": validation
            }
    
    def _generate_code_from_requirements(self, requirements: str) -> Dict[str, str]:
        """Generate Python code based on requirements."""
        # Analyze requirements to determine what type of application to create
        req_lower = requirements.lower()
        
        if any(word in req_lower for word in ['calculator', 'math', 'calculate', 'add', 'subtract', 'multiply', 'divide']):
            return self._generate_calculator_code()
        elif any(word in req_lower for word in ['todo', 'task', 'list', 'manage']):
            return self._generate_todo_app_code()
        elif any(word in req_lower for word in ['web', 'api', 'server', 'flask', 'fastapi']):
            return self._generate_web_api_code()
        elif any(word in req_lower for word in ['gui', 'tkinter', 'interface', 'window']):
            return self._generate_gui_app_code()
        elif any(word in req_lower for word in ['data', 'analysis', 'csv', 'pandas']):
            return self._generate_data_analysis_code()
        else:
            # Default: create a simple utility based on requirements
            return self._generate_generic_utility_code(requirements)
    
    def _generate_calculator_code(self) -> Dict[str, str]:
        """Generate a calculator application."""
        return {
            "calculator.py": '''#!/usr/bin/env python3
"""
Simple Calculator Application
Supports basic arithmetic operations: addition, subtraction, multiplication, division
"""

import logging
from typing import Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Calculator:
    """A simple calculator class with basic arithmetic operations."""
    
    def __init__(self):
        """Initialize the calculator."""
        logger.info("Calculator initialized")
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        result = a + b
        logger.info(f"Addition: {a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Difference of a and b
        """
        result = a - b
        logger.info(f"Subtraction: {a} - {b} = {result}")
        return result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        result = a * b
        logger.info(f"Multiplication: {a} * {b} = {result}")
        return result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Divide two numbers.
        
        Args:
            a: Dividend
            b: Divisor
            
        Returns:
            Quotient of a and b
            
        Raises:
            ValueError: If divisor is zero
        """
        if b == 0:
            logger.error("Division by zero attempted")
            raise ValueError("Cannot divide by zero")
        
        result = a / b
        logger.info(f"Division: {a} / {b} = {result}")
        return result


def main():
    """Main function to run the calculator interactively."""
    calc = Calculator()
    
    print("Simple Calculator")
    print("Operations: +, -, *, /")
    print("Type 'quit' to exit")
    
    while True:
        try:
            user_input = input("\\nEnter calculation (e.g., 5 + 3): ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            # Parse the input
            parts = user_input.split()
            if len(parts) != 3:
                print("Invalid format. Use: number operator number")
                continue
            
            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])
            
            # Perform calculation
            if operator == '+':
                result = calc.add(num1, num2)
            elif operator == '-':
                result = calc.subtract(num1, num2)
            elif operator == '*':
                result = calc.multiply(num1, num2)
            elif operator == '/':
                result = calc.divide(num1, num2)
            else:
                print(f"Unknown operator: {operator}")
                continue
            
            print(f"Result: {result}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
''',
            "test_calculator.py": '''#!/usr/bin/env python3
"""
Unit tests for the Calculator class
"""

import unittest
from calculator import Calculator


class TestCalculator(unittest.TestCase):
    """Test cases for Calculator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.calc = Calculator()
    
    def test_add(self):
        """Test addition operation."""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(0, 0), 0)
        self.assertAlmostEqual(self.calc.add(0.1, 0.2), 0.3, places=7)
    
    def test_subtract(self):
        """Test subtraction operation."""
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertEqual(self.calc.subtract(1, 1), 0)
        self.assertEqual(self.calc.subtract(-1, -1), 0)
        self.assertAlmostEqual(self.calc.subtract(0.3, 0.1), 0.2, places=7)
    
    def test_multiply(self):
        """Test multiplication operation."""
        self.assertEqual(self.calc.multiply(3, 4), 12)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
        self.assertEqual(self.calc.multiply(0, 5), 0)
        self.assertAlmostEqual(self.calc.multiply(0.5, 0.4), 0.2, places=7)
    
    def test_divide(self):
        """Test division operation."""
        self.assertEqual(self.calc.divide(10, 2), 5)
        self.assertEqual(self.calc.divide(-6, 3), -2)
        self.assertAlmostEqual(self.calc.divide(1, 3), 0.3333333333333333, places=7)
    
    def test_divide_by_zero(self):
        """Test division by zero raises ValueError."""
        with self.assertRaises(ValueError):
            self.calc.divide(5, 0)


if __name__ == "__main__":
    unittest.main()
''',
            "requirements.txt": '''# Calculator Application Requirements
# No external dependencies required - uses only Python standard library
'''
        }
    
    def _generate_todo_app_code(self) -> Dict[str, str]:
        """Generate a todo application."""
        return {
            "todo_app.py": '''#!/usr/bin/env python3
"""
Simple Todo List Application
Manage your tasks with add, remove, list, and mark complete functionality
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Task:
    """Represents a single task in the todo list."""
    
    def __init__(self, title: str, description: str = "", priority: str = "medium"):
        """Initialize a new task.
        
        Args:
            title: Task title
            description: Optional task description
            priority: Task priority (low, medium, high)
        """
        self.id = int(datetime.now().timestamp() * 1000)  # Unique ID
        self.title = title
        self.description = description
        self.priority = priority.lower()
        self.completed = False
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None
    
    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True
        self.completed_at = datetime.now().isoformat()
        logger.info(f"Task '{self.title}' marked as complete")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(data['title'], data.get('description', ''), data.get('priority', 'medium'))
        task.id = data['id']
        task.completed = data.get('completed', False)
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.completed_at = data.get('completed_at')
        return task


class TodoApp:
    """Main todo application class."""
    
    def __init__(self, filename: str = "tasks.json"):
        """Initialize the todo application.
        
        Args:
            filename: JSON file to store tasks
        """
        self.filename = filename
        self.tasks: List[Task] = []
        self.load_tasks()
        logger.info("Todo application initialized")
    
    def add_task(self, title: str, description: str = "", priority: str = "medium") -> Task:
        """Add a new task.
        
        Args:
            title: Task title
            description: Optional task description
            priority: Task priority
            
        Returns:
            The created task
        """
        task = Task(title, description, priority)
        self.tasks.append(task)
        self.save_tasks()
        logger.info(f"Added new task: {title}")
        return task
    
    def remove_task(self, task_id: int) -> bool:
        """Remove a task by ID.
        
        Args:
            task_id: ID of task to remove
            
        Returns:
            True if task was removed, False if not found
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                removed_task = self.tasks.pop(i)
                self.save_tasks()
                logger.info(f"Removed task: {removed_task.title}")
                return True
        return False
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed.
        
        Args:
            task_id: ID of task to complete
            
        Returns:
            True if task was completed, False if not found
        """
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                self.save_tasks()
                return True
        return False
    
    def list_tasks(self, show_completed: bool = True) -> List[Task]:
        """List all tasks.
        
        Args:
            show_completed: Whether to include completed tasks
            
        Returns:
            List of tasks
        """
        if show_completed:
            return self.tasks
        return [task for task in self.tasks if not task.completed]
    
    def save_tasks(self):
        """Save tasks to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2)
            logger.debug(f"Tasks saved to {self.filename}")
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")
    
    def load_tasks(self):
        """Load tasks from JSON file."""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(task_data) for task_data in data]
            logger.info(f"Loaded {len(self.tasks)} tasks from {self.filename}")
        except FileNotFoundError:
            logger.info("No existing task file found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")


def main():
    """Main function to run the todo app interactively."""
    app = TodoApp()
    
    print("Todo List Application")
    print("Commands: add, list, complete, remove, quit")
    
    while True:
        try:
            command = input("\\n> ").strip().lower()
            
            if command == 'quit':
                print("Goodbye!")
                break
            
            elif command == 'add':
                title = input("Task title: ").strip()
                if not title:
                    print("Title cannot be empty")
                    continue
                
                description = input("Description (optional): ").strip()
                priority = input("Priority (low/medium/high) [medium]: ").strip() or "medium"
                
                task = app.add_task(title, description, priority)
                print(f"Added task: {task.title} (ID: {task.id})")
            
            elif command == 'list':
                tasks = app.list_tasks()
                if not tasks:
                    print("No tasks found")
                else:
                    print("\\nTasks:")
                    for task in tasks:
                        status = "✓" if task.completed else "○"
                        print(f"  {status} [{task.id}] {task.title} ({task.priority})")
                        if task.description:
                            print(f"      {task.description}")
            
            elif command == 'complete':
                try:
                    task_id = int(input("Task ID to complete: "))
                    if app.complete_task(task_id):
                        print("Task marked as complete")
                    else:
                        print("Task not found")
                except ValueError:
                    print("Invalid task ID")
            
            elif command == 'remove':
                try:
                    task_id = int(input("Task ID to remove: "))
                    if app.remove_task(task_id):
                        print("Task removed")
                    else:
                        print("Task not found")
                except ValueError:
                    print("Invalid task ID")
            
            else:
                print("Unknown command. Available: add, list, complete, remove, quit")
        
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
'''
        }
    
    def _generate_generic_utility_code(self, requirements: str) -> Dict[str, str]:
        """Generate a generic utility based on requirements."""
        return {
            "utility.py": f'''#!/usr/bin/env python3
"""
Custom Utility Application
Generated based on requirements: {requirements}
"""

import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CustomUtility:
    """A custom utility class based on user requirements."""
    
    def __init__(self):
        """Initialize the utility."""
        logger.info("Custom utility initialized")
        self.requirements = """{requirements}"""
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data according to requirements.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed result
        """
        logger.info(f"Processing input: {{input_data}}")
        
        # Basic processing logic - customize based on requirements
        result = {{
            "input": input_data,
            "processed": True,
            "requirements": self.requirements,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }}
        
        logger.info("Processing completed")
        return result
    
    def get_info(self) -> Dict[str, str]:
        """Get information about this utility."""
        return {{
            "name": "Custom Utility",
            "requirements": self.requirements,
            "version": "1.0.0"
        }}


def main():
    """Main function to run the utility."""
    utility = CustomUtility()
    
    print("Custom Utility Application")
    print(f"Requirements: {{utility.requirements}}")
    print("Type 'quit' to exit")
    
    while True:
        try:
            user_input = input("\\nEnter input: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            result = utility.process(user_input)
            print(f"Result: {{result}}")
            
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {{e}}")


if __name__ == "__main__":
    main()
'''
        }


# Backward compatibility - keep the old class for existing code
class PythonCoder:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Python Coding Agent."""
        return {
            "name": "PythonCoder",
            "system_message": PythonCoderAgent.get_metadata().description,
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 2,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured PythonCoder agent."""
        agent_instance = PythonCoderAgent(llm_config)
        return agent_instance.create_agent()
