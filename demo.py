"""
Demo script to showcase the Multi-Agent Framework capabilities.
"""

import sys
import os
import asyncio

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.pipeline_service import PipelineService

async def run_demo():
    """Run a simple demo of the framework."""
    print("🤖 Multi-Agent Framework Demo")
    print("=" * 50)
    
    # Simple demo input
    demo_input = "Create a simple calculator that can perform basic arithmetic operations (addition, subtraction, multiplication, division) with a command-line interface."
    
    print(f"Demo Input: {demo_input}")
    print("\nValidating input...")
    
    # Initialize pipeline service
    pipeline_service = PipelineService()
    
    try:
        # Validate input
        validation = await pipeline_service.validate_input(demo_input)
        print(f"✅ Input validation passed: {validation.is_valid}")
        
        if validation.warnings:
            print("Warnings:")
            for warning in validation.warnings:
                print(f"  - {warning}")
        
        if validation.suggestions:
            print("Suggestions:")
            for suggestion in validation.suggestions:
                print(f"  - {suggestion}")
        
        # Get pipeline status
        pipeline_status = await pipeline_service.get_pipeline_status()
        print(f"\n📊 Pipeline Status:")
        print(f"  - Agent Manager: {pipeline_status['current_progress']['agent_manager']}")
        print(f"  - Available Agents: {pipeline_status['current_progress']['available_agents']}")
        print(f"  - Pipeline Config: {pipeline_status['current_progress']['pipeline_config']}")
        print(f"  - Total Runs: {pipeline_status['total_runs']}")
        print(f"  - Successful Runs: {pipeline_status['successful_runs']}")
        
        # Get agent info
        agent_info = await pipeline_service.get_agent_info()
        print(f"\n🤖 Agent Information:")
        print(f"  - Agent Manager Version: {agent_info['agent_manager']}")
        print(f"  - Total Agents: {agent_info['total_agents']}")
        print(f"  - Status: {agent_info['status']}")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        print("This might indicate the framework needs to be properly initialized.")
    
    print("\n🎯 Framework is ready for full pipeline execution!")
    print("\nTo run the complete pipeline:")
    print("1. Start the backend: python start_backend.py")
    print("2. Start the frontend: python start_frontend.py")
    print("3. Open your browser to the Streamlit interface")
    print("\nOr use the API directly:")
    print(f'curl -X POST "http://localhost:8000/api/v1/pipeline/generate" -H "Content-Type: application/json" -d \'{{"user_input": "{demo_input}"}}\'')

def main():
    """Main function to run the demo."""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
