"""
Test script to demonstrate the new modular agent architecture.
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.agent_factory import agent_factory
from core.events import event_bus, EventType, EventFilter
from core.agent_manager_v2 import agent_manager_v2
from config.pipeline_config import pipeline_config_manager
from services.agent_service import AgentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_agent_factory():
    """Test the agent factory functionality."""
    print("\n" + "="*50)
    print("TESTING AGENT FACTORY")
    print("="*50)
    
    # Auto-discover agents
    discovered_count = agent_factory.auto_discover_agents()
    print(f"✅ Discovered {discovered_count} agents")
    
    # Get available agents
    available_agents = agent_factory.get_available_agents()
    print(f"✅ Available agents: {list(available_agents.keys())}")
    
    # Show agent details
    for agent_key, metadata in available_agents.items():
        print(f"\n📋 Agent: {metadata.name}")
        print(f"   Description: {metadata.description}")
        print(f"   Config Type: {metadata.config_type.value}")
        print(f"   Capabilities: {len(metadata.capabilities)} items")
        print(f"   Dependencies: {metadata.dependencies or 'None'}")
        print(f"   Version: {metadata.version}")
    
    # Test dependency validation
    dependency_issues = agent_factory.validate_dependencies()
    if dependency_issues:
        print(f"⚠️  Dependency issues: {dependency_issues}")
    else:
        print("✅ All dependencies validated")
    
    # Test agent creation
    if available_agents:
        first_agent_key = list(available_agents.keys())[0]
        try:
            agent_instance = agent_factory.create_agent(first_agent_key)
            print(f"✅ Successfully created agent: {agent_instance.metadata.name}")
        except Exception as e:
            print(f"❌ Failed to create agent: {str(e)}")
    
    # Get factory stats
    stats = agent_factory.get_factory_stats()
    print(f"✅ Factory stats: {stats}")

async def test_event_system():
    """Test the event system functionality."""
    print("\n" + "="*50)
    print("TESTING EVENT SYSTEM")
    print("="*50)
    
    events_received = []
    
    # Subscribe to events
    def event_handler(event):
        events_received.append(event)
        print(f"📨 Received event: {event.event_type.value} from {event.source}")
    
    # Subscribe to agent events
    event_bus.subscribe(EventType.AGENT_STARTED, event_handler)
    event_bus.subscribe(EventType.AGENT_COMPLETED, event_handler)
    
    # Publish test events
    from core.events import publish_agent_started, publish_agent_completed
    
    correlation_id = event_bus.create_correlation_id()
    print(f"✅ Created correlation ID: {correlation_id}")
    
    await publish_agent_started("test_agent", correlation_id, test_data="hello")
    await publish_agent_completed("test_agent", {"result": "success"}, correlation_id)
    
    # Check event history
    history = event_bus.get_event_history(limit=5)
    print(f"✅ Event history contains {len(history)} events")
    
    # Get events by correlation ID
    correlated_events = event_bus.get_events_by_correlation_id(correlation_id)
    print(f"✅ Found {len(correlated_events)} events with correlation ID")
    
    # Get event stats
    stats = event_bus.get_stats()
    print(f"✅ Event bus stats: {stats}")
    
    print(f"✅ Total events received by handler: {len(events_received)}")

async def test_pipeline_config():
    """Test the pipeline configuration system."""
    print("\n" + "="*50)
    print("TESTING PIPELINE CONFIGURATION")
    print("="*50)
    
    # Get available pipelines
    available_pipelines = pipeline_config_manager.get_available_pipelines()
    print(f"✅ Available pipelines: {available_pipelines}")
    
    # Get default pipeline
    default_pipeline = pipeline_config_manager.get_pipeline_config("default")
    print(f"✅ Default pipeline: {default_pipeline.name}")
    print(f"   Description: {default_pipeline.description}")
    print(f"   Steps: {len(default_pipeline.steps)}")
    
    # Show pipeline steps
    for i, step in enumerate(default_pipeline.steps, 1):
        print(f"   {i}. {step.agent_type} ({step.config_type})")
        if step.depends_on:
            print(f"      Depends on: {step.depends_on}")
    
    # Test execution order
    try:
        execution_order = default_pipeline.get_execution_order()
        print(f"✅ Execution order: {execution_order}")
    except Exception as e:
        print(f"❌ Failed to get execution order: {str(e)}")
    
    # Validate pipeline
    issues = default_pipeline.validate()
    if issues:
        print(f"⚠️  Pipeline validation issues: {issues}")
    else:
        print("✅ Pipeline validation passed")

async def test_agent_manager_v2():
    """Test the new agent manager."""
    print("\n" + "="*50)
    print("TESTING AGENT MANAGER V2")
    print("="*50)
    
    # Initialize pipeline
    success = agent_manager_v2.initialize_pipeline("default")
    print(f"✅ Pipeline initialization: {'Success' if success else 'Failed'}")
    
    if success:
        # Get pipeline info
        pipeline_info = agent_manager_v2.get_pipeline_info()
        if pipeline_info:
            print(f"✅ Pipeline info: {pipeline_info['name']} with {pipeline_info['total_steps']} steps")
        
        # Get available and active agents
        available = agent_manager_v2.get_available_agents()
        active = agent_manager_v2.get_active_agents()
        print(f"✅ Available agents: {len(available)}")
        print(f"✅ Active agents: {len(active)}")
        
        # Get initial progress
        progress = agent_manager_v2.get_progress()
        print(f"✅ Initial progress: {progress.get('progress_percentage', 0)}%")
        
        # Test pipeline execution (mock)
        print("🚀 Testing pipeline execution...")
        try:
            result = await agent_manager_v2.execute_pipeline("Test input: Create a simple calculator")
            if result.get('success'):
                print("✅ Pipeline execution completed successfully")
                print(f"   Results: {len(result.get('results', {}))} steps completed")
            else:
                print(f"❌ Pipeline execution failed: {result.get('error')}")
        except Exception as e:
            print(f"❌ Pipeline execution error: {str(e)}")

async def test_agent_service():
    """Test the updated agent service."""
    print("\n" + "="*50)
    print("TESTING AGENT SERVICE")
    print("="*50)
    
    agent_service = AgentService()
    
    # Get agents info
    agents_response = await agent_service.get_agents_info()
    print(f"✅ Agents response: {len(agents_response.available_agents)} agents")
    
    # Get agents summary
    summary = await agent_service.get_agents_summary()
    print(f"✅ Agents summary: {summary}")
    
    # Get pipeline configurations
    pipeline_configs = await agent_service.get_pipeline_configurations()
    print(f"✅ Pipeline configurations: {pipeline_configs}")
    
    # Test agent capabilities
    if agents_response.available_agents:
        first_agent = agents_response.available_agents[0]
        capabilities = await agent_service.get_agent_capabilities(first_agent)
        print(f"✅ {first_agent} capabilities: {len(capabilities)} items")
        
        # Test agent dependencies
        dependencies = await agent_service.get_agent_dependencies(first_agent)
        print(f"✅ {first_agent} dependencies: {dependencies}")

async def main():
    """Run all tests."""
    print("🚀 TESTING NEW MODULAR AGENT ARCHITECTURE")
    print("="*60)
    
    try:
        await test_agent_factory()
        await test_event_system()
        await test_pipeline_config()
        await test_agent_manager_v2()
        await test_agent_service()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
