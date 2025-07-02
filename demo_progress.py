#!/usr/bin/env python3
"""
Demo script to showcase the enhanced dynamic progress features.
This script demonstrates the real-time progress tracking capabilities.
"""

import time
import threading
from datetime import datetime
from core.utils import ProgressTracker, RealTimeProgressManager

def simulate_multi_agent_pipeline():
    """Simulate a multi-agent pipeline with realistic progress updates."""
    
    # Create progress tracker
    tracker = ProgressTracker()
    
    # Set up pipeline steps
    steps = [
        ("requirements_analysis", "Analyzing requirements from user input", 25.0),
        ("code_generation", "Generating Python code from requirements", 45.0),
        ("code_review", "Reviewing code for quality and security", 30.0),
        ("documentation", "Creating comprehensive documentation", 20.0),
        ("test_generation", "Generating test cases", 25.0),
        ("deployment_config", "Creating deployment configurations", 15.0),
        ("ui_generation", "Creating Streamlit user interface", 20.0)
    ]
    
    for step_name, description, estimated_duration in steps:
        tracker.add_step(step_name, description, estimated_duration)
    
    # Add progress callback to show updates
    def progress_callback(progress_data):
        print(f"\n📊 Progress Update: {progress_data['progress_percentage']:.1f}%")
        current_step = progress_data.get('current_step_info')
        if current_step:
            print(f"🔄 Current: {current_step['description']}")
        
        # Show recent logs
        recent_logs = progress_data.get('logs', [])
        if recent_logs:
            print("📝 Recent Activity:")
            for log in recent_logs[-3:]:  # Show last 3 logs
                timestamp = log['timestamp'][:19].replace('T', ' ')
                agent = log.get('agent_name', 'System')
                print(f"   [{timestamp}] {agent}: {log['message']}")
    
    tracker.add_progress_callback(progress_callback)
    
    print("🚀 Starting Multi-Agent Pipeline Demo")
    print("=" * 60)
    
    # Simulate each step
    for i, (step_name, description, estimated_duration) in enumerate(steps):
        agent_name = {
            0: "requirement_analyst",
            1: "python_coder", 
            2: "code_reviewer",
            3: "documentation_writer",
            4: "test_generator",
            5: "deployment_engineer",
            6: "ui_designer"
        }.get(i, "system")
        
        # Start step
        tracker.start_step(i, agent_name)
        
        # Simulate substeps for first few steps
        if i == 0:  # Requirements analysis
            substeps = [
                ("parsing_input", "Parsing user input", 0.3),
                ("analyzing_requirements", "Analyzing requirements", 0.5),
                ("structuring_output", "Structuring output", 0.2)
            ]
            
            for substep_name, substep_desc, substep_ratio in substeps:
                tracker.add_substep(i, substep_name, substep_desc)
                tracker.update_substep(i, substep_name, "running")
                
                # Simulate substep progress
                substep_duration = estimated_duration * substep_ratio
                steps_in_substep = 5
                for step in range(steps_in_substep):
                    time.sleep(substep_duration / steps_in_substep)
                    progress = (step + 1) / steps_in_substep * 100 * substep_ratio
                    tracker.update_step_progress(i, progress, f"Processing {substep_desc.lower()}")
                
                tracker.update_substep(i, substep_name, "completed")
        
        elif i == 1:  # Code generation
            substeps = [
                ("preparing_requirements", "Preparing requirements", 0.1),
                ("generating_code", "Generating code", 0.7),
                ("extracting_code", "Extracting code blocks", 0.2)
            ]
            
            for substep_name, substep_desc, substep_ratio in substeps:
                tracker.add_substep(i, substep_name, substep_desc)
                tracker.update_substep(i, substep_name, "running")
                
                # Simulate substep progress
                substep_duration = estimated_duration * substep_ratio
                steps_in_substep = 8 if substep_name == "generating_code" else 3
                for step in range(steps_in_substep):
                    time.sleep(substep_duration / steps_in_substep)
                    progress = sum(s[2] for s in substeps[:substeps.index((substep_name, substep_desc, substep_ratio))]) * 100
                    progress += (step + 1) / steps_in_substep * 100 * substep_ratio
                    tracker.update_step_progress(i, progress, f"Processing {substep_desc.lower()}")
                
                tracker.update_substep(i, substep_name, "completed")
        
        else:
            # Simulate regular step progress
            steps_in_step = 10
            for step in range(steps_in_step):
                time.sleep(estimated_duration / steps_in_step)
                progress = (step + 1) / steps_in_step * 100
                tracker.update_step_progress(i, progress, f"Processing {description.lower()}")
        
        # Complete step
        tracker.complete_step(i, True, f"Successfully completed {description.lower()}")
        
        # Brief pause between steps
        time.sleep(0.5)
    
    print("\n🎉 Pipeline completed successfully!")
    print("=" * 60)
    
    # Show final progress summary
    final_progress = tracker.get_progress()
    print(f"📊 Final Statistics:")
    print(f"   Total Steps: {final_progress['total_steps']}")
    print(f"   Completed: {final_progress['completed_steps']}")
    print(f"   Total Time: {final_progress['elapsed_time']:.1f}s")
    print(f"   Success Rate: 100%")
    
    return tracker

def demo_real_time_updates():
    """Demo real-time progress updates with callbacks."""
    
    print("\n🔄 Real-Time Progress Updates Demo")
    print("=" * 60)
    
    tracker = ProgressTracker()
    
    # Add some steps
    tracker.add_step("step1", "Processing data", 10.0)
    tracker.add_step("step2", "Analyzing results", 15.0)
    tracker.add_step("step3", "Generating output", 8.0)
    
    # Real-time update callback
    def real_time_callback(progress_data):
        current_step = progress_data.get('current_step_info')
        if current_step and current_step['status'] == 'running':
            progress_bar = "█" * int(current_step['progress_percentage'] / 5)
            progress_bar += "░" * (20 - int(current_step['progress_percentage'] / 5))
            print(f"\r🔄 {current_step['name']}: [{progress_bar}] {current_step['progress_percentage']:.1f}%", end="", flush=True)
    
    tracker.add_progress_callback(real_time_callback)
    
    # Simulate steps with real-time updates
    for i in range(3):
        tracker.start_step(i, f"agent_{i+1}")
        
        # Simulate gradual progress
        for progress in range(0, 101, 5):
            tracker.update_step_progress(i, progress)
            time.sleep(0.1)
        
        tracker.complete_step(i, True)
        print()  # New line after progress bar
    
    print("✅ Real-time demo completed!")

def demo_agent_activities():
    """Demo agent activity monitoring."""
    
    print("\n🤖 Agent Activity Monitoring Demo")
    print("=" * 60)
    
    tracker = ProgressTracker()
    
    # Add steps with different agents
    agents = [
        ("requirement_analyst", "Analyzing requirements"),
        ("python_coder", "Generating code"),
        ("code_reviewer", "Reviewing code"),
        ("documentation_writer", "Writing documentation")
    ]
    
    for i, (agent_name, description) in enumerate(agents):
        tracker.add_step(f"step_{i+1}", description, 5.0)
    
    # Activity monitoring callback
    def activity_callback(progress_data):
        activities = progress_data.get('agent_activities', {})
        if activities:
            print("\n🤖 Agent Activities:")
            for agent_name, activity in activities.items():
                status_icon = {"active": "🔄", "completed": "✅", "failed": "❌"}.get(activity['status'], "❓")
                print(f"   {status_icon} {agent_name}: {activity['status']}")
    
    tracker.add_progress_callback(activity_callback)
    
    # Simulate concurrent agent activities
    for i, (agent_name, description) in enumerate(agents):
        tracker.start_step(i, agent_name)
        
        # Simulate work
        for progress in range(0, 101, 20):
            tracker.update_step_progress(i, progress, f"{description} - {progress}% complete")
            time.sleep(0.3)
        
        tracker.complete_step(i, True, f"Completed {description}")
        time.sleep(0.5)
    
    print("\n✅ Agent activity demo completed!")

def demo_error_handling():
    """Demo error handling and failure scenarios."""
    
    print("\n❌ Error Handling Demo")
    print("=" * 60)
    
    tracker = ProgressTracker()
    
    # Add steps, some will fail
    tracker.add_step("step1", "Processing input", 5.0)
    tracker.add_step("step2", "Critical operation (will fail)", 8.0)
    tracker.add_step("step3", "Recovery operation", 3.0)
    
    def error_callback(progress_data):
        if progress_data['has_failures']:
            print(f"⚠️  Pipeline has failures! Failed steps: {progress_data['failed_steps']}")
    
    tracker.add_progress_callback(error_callback)
    
    # Step 1: Success
    tracker.start_step(0, "processor")
    for progress in range(0, 101, 25):
        tracker.update_step_progress(0, progress)
        time.sleep(0.2)
    tracker.complete_step(0, True, "Input processed successfully")
    
    # Step 2: Failure
    tracker.start_step(1, "critical_agent")
    for progress in range(0, 61, 20):
        tracker.update_step_progress(1, progress)
        time.sleep(0.2)
    tracker.complete_step(1, False, "Critical operation failed due to network timeout")
    
    # Step 3: Recovery
    tracker.start_step(2, "recovery_agent")
    for progress in range(0, 101, 33):
        tracker.update_step_progress(2, progress)
        time.sleep(0.2)
    tracker.complete_step(2, True, "Recovery completed successfully")
    
    # Show final status
    final_progress = tracker.get_progress()
    print(f"\n📊 Final Status:")
    print(f"   Completed: {final_progress['completed_steps']}/{final_progress['total_steps']}")
    print(f"   Failed: {final_progress['failed_steps']}")
    print(f"   Success Rate: {(final_progress['completed_steps']/final_progress['total_steps']*100):.1f}%")

if __name__ == "__main__":
    print("🎯 Multi-Agent Framework - Dynamic Progress Demo")
    print("=" * 60)
    print("This demo showcases the enhanced progress tracking features:")
    print("• Real-time progress updates")
    print("• Detailed step-by-step tracking")
    print("• Agent activity monitoring")
    print("• Live logging with timestamps")
    print("• Error handling and recovery")
    print("• Estimated time remaining")
    print("=" * 60)
    
    try:
        # Run all demos
        simulate_multi_agent_pipeline()
        time.sleep(2)
        
        demo_real_time_updates()
        time.sleep(2)
        
        demo_agent_activities()
        time.sleep(2)
        
        demo_error_handling()
        
        print("\n🎉 All demos completed successfully!")
        print("🚀 Try running the Streamlit app to see the full UI experience:")
        print("   python -m streamlit run streamlit_app.py")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
