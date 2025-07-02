"""
Simple test script to verify the Multi-Agent Framework is working correctly.
"""

import os
import sys
import traceback
from typing import Dict, Any

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test core imports
        from config.model_config import model_config
        from config.agent_config import agent_config
        from core.utils import setup_logging, ProgressTracker
        from core.agent_manager import AgentManager
        from core.pipeline import pipeline
        
        print("✅ All core modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    
    try:
        from config.model_config import model_config
        
        # Check if OpenAI API key is configured
        if not model_config.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment")
            print("   Please set your OpenAI API key in the .env file")
            return False
        
        print("✅ Environment configuration looks good")
        return True
        
    except Exception as e:
        print(f"❌ Environment configuration error: {e}")
        return False

def test_agent_initialization():
    """Test that agents can be initialized."""
    print("\nTesting agent initialization...")
    
    try:
        from core.agent_manager import AgentManager
        
        # This will test agent initialization
        agent_manager = AgentManager()
        
        # Check if agents are loaded
        expected_agents = [
            'requirement_analyst', 'python_coder', 'code_reviewer',
            'documentation_writer', 'test_generator', 'deployment_engineer',
            'ui_designer', 'user_proxy'
        ]
        
        for agent_name in expected_agents:
            if agent_name not in agent_manager.agents:
                print(f"❌ Agent '{agent_name}' not found")
                return False
        
        print(f"✅ All {len(expected_agents)} agents initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        traceback.print_exc()
        return False

def test_pipeline_validation():
    """Test pipeline input validation."""
    print("\nTesting pipeline validation...")
    
    try:
        from core.pipeline import pipeline
        
        # Test input validation
        test_inputs = [
            ("", False),  # Empty input should have warnings
            ("a", False),  # Very short input should have warnings
            ("Create a simple calculator application with basic arithmetic operations", True),  # Good input
        ]
        
        for test_input, should_be_good in test_inputs:
            validation = pipeline.validate_input(test_input)
            
            if should_be_good and validation['warnings']:
                print(f"❌ Good input '{test_input[:30]}...' has unexpected warnings")
                return False
            elif not should_be_good and not validation['warnings']:
                print(f"❌ Bad input '{test_input[:30]}...' should have warnings")
                return False
        
        print("✅ Pipeline validation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline validation error: {e}")
        return False

def test_utilities():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from core.utils import (
            setup_logging, ensure_directory, generate_timestamp,
            validate_requirements, ProgressTracker
        )
        
        # Test logging setup
        logger = setup_logging()
        
        # Test directory creation
        test_dir = "test_temp_dir"
        ensure_directory(test_dir)
        if not os.path.exists(test_dir):
            print("❌ Directory creation failed")
            return False
        
        # Clean up
        os.rmdir(test_dir)
        
        # Test timestamp generation
        timestamp = generate_timestamp()
        if len(timestamp) != 15:  # Format: YYYYMMDD_HHMMSS
            print("❌ Timestamp format incorrect")
            return False
        
        # Test progress tracker
        tracker = ProgressTracker()
        tracker.add_step("test_step", "Testing step")
        tracker.start_step(0)
        tracker.complete_step(0, True)
        
        progress = tracker.get_progress()
        if progress['completed_steps'] != 1:
            print("❌ Progress tracker not working correctly")
            return False
        
        print("✅ Utility functions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Utility functions error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config.model_config import model_config
        from config.agent_config import agent_config
        
        # Test model config
        llm_config = model_config.get_llm_config()
        if 'config_list' not in llm_config:
            print("❌ LLM config format incorrect")
            return False
        
        # Test agent configs
        req_config = agent_config.get_requirement_agent_config()
        if 'name' not in req_config or 'system_message' not in req_config:
            print("❌ Agent config format incorrect")
            return False
        
        print("✅ Configuration loading working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def run_all_tests():
    """Run all tests and return overall result."""
    print("🤖 Multi-Agent Framework Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_configuration,
        test_utilities,
        test_pipeline_validation,
        test_agent_initialization,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The framework is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python main.py web' to launch the web interface")
        print("2. Or try 'python main.py generate \"your description here\"'")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("- Make sure you have set OPENAI_API_KEY in your .env file")
        print("- Ensure all dependencies are installed: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
