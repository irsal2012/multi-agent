"""
Demo script to showcase the Multi-Agent Framework capabilities.
"""

from core.pipeline import pipeline

def run_demo():
    """Run a simple demo of the framework."""
    print("🤖 Multi-Agent Framework Demo")
    print("=" * 50)
    
    # Simple demo input
    demo_input = "Create a simple calculator that can perform basic arithmetic operations (addition, subtraction, multiplication, division) with a command-line interface."
    
    print(f"Demo Input: {demo_input}")
    print("\nValidating input...")
    
    # Validate input
    validation = pipeline.validate_input(demo_input)
    print(f"✅ Input validation passed")
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['suggestions']:
        print("Suggestions:")
        for suggestion in validation['suggestions']:
            print(f"  - {suggestion}")
    
    print("\n🎯 Framework is ready for full pipeline execution!")
    print("\nTo run the complete pipeline:")
    print(f'python main.py generate "{demo_input}"')
    print("\nOr launch the web interface:")
    print("python main.py web")

if __name__ == "__main__":
    run_demo()
