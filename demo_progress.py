"""
Demo script to show real-time progress updates working correctly.
This demonstrates the fixed progress tracking system.
"""

import streamlit as st
import time
import threading
from datetime import datetime
from typing import Dict, Any

# Configure page
st.set_page_config(
    page_title="Progress Demo - Multi-Agent Code Generator",
    page_icon="🚀",
    layout="wide"
)

def simulate_pipeline_step(step_name: str, duration: float, progress_container):
    """Simulate a pipeline step with progress updates."""
    
    # Update step to running
    progress_container.info(f"🔄 **{step_name}** - Running")
    
    # Simulate work with progress updates
    for i in range(int(duration * 10)):  # 10 updates per second
        time.sleep(0.1)
        progress = (i + 1) / (duration * 10) * 100
        progress_container.info(f"🔄 **{step_name}** - Running ({progress:.0f}%)")
    
    # Mark as completed
    progress_container.success(f"✅ **{step_name}** - Completed ({duration:.1f}s)")

def run_demo_pipeline():
    """Run a demo pipeline with real-time progress updates."""
    
    st.title("🚀 Real-Time Progress Demo")
    st.markdown("This demo shows how the progress tracking should work with incremental updates.")
    
    # Initialize session state
    if 'demo_running' not in st.session_state:
        st.session_state.demo_running = False
    
    # Start button
    if st.button("🚀 Start Demo Pipeline", disabled=st.session_state.demo_running):
        st.session_state.demo_running = True
        st.rerun()
    
    if st.session_state.demo_running:
        # Create progress interface
        st.subheader("🚀 Generation in Progress")
        
        # Overall progress
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        # Pipeline steps
        st.markdown("### 📋 Pipeline Steps")
        
        steps = [
            ("Requirements Analysis", 3.0),
            ("Code Generation", 5.0),
            ("Code Review", 3.0),
            ("Documentation", 2.0),
            ("Test Generation", 2.5),
            ("Deployment Config", 1.5),
            ("UI Generation", 2.0)
        ]
        
        # Create placeholders for each step
        step_containers = []
        for i, (step_name, _) in enumerate(steps):
            container = st.empty()
            container.info(f"⏳ **{i+1}. {step_name}** - Waiting")
            step_containers.append(container)
        
        # Run steps with real-time updates
        total_duration = sum(duration for _, duration in steps)
        elapsed_time = 0
        
        for i, (step_name, duration) in enumerate(steps):
            # Update overall status
            status_text.info(f"🔄 **Currently running: {step_name}**")
            
            # Update overall progress
            progress_before = elapsed_time / total_duration
            overall_progress.progress(progress_before)
            
            # Run the step with updates
            start_time = time.time()
            step_containers[i].info(f"🔄 **{i+1}. {step_name}** - Running")
            
            # Simulate step execution with progress updates
            step_duration = duration
            for j in range(int(step_duration * 5)):  # 5 updates per second
                time.sleep(0.2)
                
                # Update step progress
                step_progress = (j + 1) / (step_duration * 5) * 100
                step_containers[i].info(f"🔄 **{i+1}. {step_name}** - Running ({step_progress:.0f}%)")
                
                # Update overall progress
                current_elapsed = elapsed_time + (time.time() - start_time)
                overall_progress.progress(min(current_elapsed / total_duration, 1.0))
                
                # Force update
                st.empty()
            
            # Mark step as completed
            actual_duration = time.time() - start_time
            step_containers[i].success(f"✅ **{i+1}. {step_name}** - Completed ({actual_duration:.1f}s)")
            elapsed_time += actual_duration
            
            # Update overall progress
            overall_progress.progress(elapsed_time / total_duration)
        
        # Final completion
        overall_progress.progress(1.0)
        status_text.success("✅ **All steps completed successfully!**")
        
        st.success("🎉 **Demo pipeline completed!**")
        st.balloons()
        
        # Reset button
        if st.button("🔄 Reset Demo"):
            st.session_state.demo_running = False
            st.rerun()

def show_fixed_approach():
    """Show the approach that should be used for real-time updates."""
    
    st.title("📋 Fixed Progress Tracking Approach")
    
    st.markdown("""
    ## The Problem
    The original implementation had these issues:
    1. **No Real-time Updates**: Progress was only shown after completion
    2. **Threading Issues**: Streamlit doesn't handle threading well for UI updates
    3. **Callback Limitations**: Progress callbacks couldn't trigger UI updates
    
    ## The Solution
    The fixed approach uses:
    1. **Incremental Progress Updates**: Each step shows progress as it runs
    2. **Direct UI Updates**: Progress is updated directly in the main thread
    3. **Step-by-Step Execution**: Each step updates its status immediately
    4. **Substep Tracking**: Detailed progress within each major step
    
    ## Key Changes Made:
    
    ### 1. Enhanced Progress Tracker
    - Added substep tracking with `add_substep()` and `update_substep()`
    - Added `update_step_progress()` for percentage updates within steps
    - Added detailed logging with `add_log()`
    
    ### 2. Real-time UI Updates
    - Progress bars update during execution, not after
    - Step status changes from "Waiting" → "Running" → "Completed"
    - Substep details shown (e.g., "Parsing input", "Analyzing requirements")
    
    ### 3. Agent Manager Integration
    - Each agent method calls progress tracker methods
    - Progress updates happen at key points during execution
    - Detailed substeps for complex operations
    
    ## Example Usage:
    ```python
    # Start a step
    self.progress_tracker.start_step(0, "requirement_analyst")
    
    # Add substeps
    self.progress_tracker.add_substep(0, "parsing_input", "Parsing user input")
    self.progress_tracker.update_substep(0, "parsing_input", "running")
    
    # Update progress percentage
    self.progress_tracker.update_step_progress(0, 30, "Analyzing requirements")
    
    # Complete substep
    self.progress_tracker.update_substep(0, "parsing_input", "completed")
    
    # Complete main step
    self.progress_tracker.complete_step(0, True, "Requirements analysis completed")
    ```
    """)

def main():
    """Main demo application."""
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Demo Navigation")
        demo_type = st.selectbox(
            "Choose demo:",
            ["Real-time Progress Demo", "Fixed Approach Explanation"]
        )
    
    if demo_type == "Real-time Progress Demo":
        run_demo_pipeline()
    else:
        show_fixed_approach()

if __name__ == "__main__":
    main()
