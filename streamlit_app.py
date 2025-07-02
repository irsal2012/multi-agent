"""
Streamlit web interface for the Multi-Agent Framework.
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any

from core.pipeline import pipeline
from core.utils import setup_logging

# Configure page
st.set_page_config(
    page_title="Multi-Agent Code Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logging
logger = setup_logging()

def main():
    """Main Streamlit application."""
    
    # Title and description
    st.title("🤖 Multi-Agent Code Generator")
    st.markdown("""
    Transform your ideas into complete Python applications using our AI-powered multi-agent system.
    Simply describe what you want to build, and our specialized agents will:
    
    - 📋 Analyze your requirements
    - 💻 Generate production-ready code
    - 🔍 Review and optimize the code
    - 📚 Create comprehensive documentation
    - 🧪 Generate test cases
    - 🚀 Create deployment configurations
    - 🎨 Build a Streamlit user interface
    """)
    
    # Sidebar for navigation and info
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Code Generator", "Pipeline Status", "Agent Information", "Project History"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This framework uses AutoGen to coordinate multiple AI agents,
        each specialized in different aspects of software development.
        """)
    
    # Route to different pages
    if page == "Code Generator":
        show_code_generator()
    elif page == "Pipeline Status":
        show_pipeline_status()
    elif page == "Agent Information":
        show_agent_info()
    elif page == "Project History":
        show_project_history()

def show_code_generator():
    """Main code generation interface."""
    
    st.header("🚀 Generate Your Application")
    
    # Quick Examples (outside form)
    st.subheader("Quick Examples")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Data Analysis Tool", use_container_width=True):
            st.session_state.example_input = "Create a data analysis tool that reads CSV files, performs statistical analysis, generates visualizations, and exports reports in PDF format."
            st.rerun()
    
    with col2:
        if st.button("🌐 Web API", use_container_width=True):
            st.session_state.example_input = "Build a REST API for a task management system with user authentication, CRUD operations for tasks, and email notifications."
            st.rerun()
    
    with col3:
        if st.button("🤖 Chatbot", use_container_width=True):
            st.session_state.example_input = "Create an intelligent chatbot that can answer questions about a knowledge base, with conversation history and context awareness."
            st.rerun()
    
    # Input form
    with st.form("code_generation_form"):
        st.subheader("Describe Your Project")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Use example if selected, otherwise use empty string
            default_input = st.session_state.get('example_input', '')
            
            user_input = st.text_area(
                "What would you like to build?",
                value=default_input,
                placeholder="Example: Create a web scraper that extracts product information from e-commerce websites, stores the data in a database, and provides a REST API to query the results.",
                height=150,
                help="Provide a detailed description of the application you want to build. Include functionality, data sources, user interactions, and any specific requirements."
            )
        
        with col2:
            project_name = st.text_input(
                "Project Name (optional)",
                placeholder="my-awesome-project",
                help="If not provided, a timestamp-based name will be generated."
            )
        
        # Validation
        if user_input:
            validation = pipeline.validate_input(user_input)
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    st.warning(f"⚠️ {warning}")
            
            if validation['suggestions']:
                with st.expander("💡 Suggestions for better results"):
                    for suggestion in validation['suggestions']:
                        st.info(suggestion)
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Generate Application",
            use_container_width=True,
            type="primary"
        )
    
    # Process submission
    if submitted and user_input:
        # Clear the example input after successful submission
        if 'example_input' in st.session_state:
            del st.session_state.example_input
        generate_application(user_input, project_name)
    elif submitted:
        st.error("Please provide a description of what you want to build.")

def generate_application(user_input: str, project_name: str = None):
    """Generate application using the multi-agent pipeline with real-time progress."""
    
    # Initialize session state for progress tracking
    if 'generation_active' not in st.session_state:
        st.session_state.generation_active = False
    
    if st.session_state.generation_active:
        st.warning("⚠️ Generation already in progress. Please wait for completion.")
        return
    
    # Set generation as active
    st.session_state.generation_active = True
    
    try:
        # Create comprehensive progress interface
        progress_container = st.container()
        
        with progress_container:
            st.subheader("🚀 Generation in Progress")
            
            # Main progress bar
            main_progress = st.progress(0)
            
            # Status and timing info
            col1, col2, col3 = st.columns(3)
            with col1:
                status_text = st.empty()
            with col2:
                elapsed_time = st.empty()
            with col3:
                eta_text = st.empty()
            
            # Current step details
            current_step_container = st.container()
            with current_step_container:
                step_header = st.empty()
                step_progress = st.empty()
                step_details = st.empty()
            
            # Agent activity monitor
            agent_container = st.container()
            with agent_container:
                st.markdown("### 🤖 Agent Activity")
                agent_status = st.empty()
            
            # Live logs
            logs_container = st.container()
            with logs_container:
                st.markdown("### 📝 Live Activity Log")
                logs_display = st.empty()
            
            # Detailed step breakdown
            steps_container = st.container()
            with steps_container:
                st.markdown("### 📋 Pipeline Steps")
                steps_display = st.empty()
        
        # Run pipeline with real-time updates
        start_time = time.time()
        
        # Create a custom progress callback for real-time updates
        def update_progress_display():
            try:
                progress_data = pipeline.get_pipeline_status()['current_progress']
                
                # Update main progress bar
                main_progress.progress(progress_data['progress_percentage'] / 100)
                
                # Update status text
                if progress_data['is_running']:
                    current_step = progress_data.get('current_step_info')
                    if current_step:
                        status_icon = get_status_icon(current_step['status'])
                        status_text.markdown(f"**{status_icon} {current_step['description']}**")
                elif progress_data['is_completed']:
                    status_text.success("✅ **Generation Completed!**")
                elif progress_data['has_failures']:
                    status_text.error("❌ **Generation Failed**")
                
                # Update timing info
                elapsed = progress_data['elapsed_time']
                elapsed_time.metric("Elapsed", f"{elapsed:.1f}s")
                
                if progress_data['estimated_remaining_time'] > 0:
                    eta_text.metric("ETA", f"{progress_data['estimated_remaining_time']:.1f}s")
                else:
                    eta_text.metric("ETA", "Calculating...")
                
                # Update current step details
                current_step = progress_data.get('current_step_info')
                if current_step:
                    step_icon = get_status_icon(current_step['status'])
                    step_header.markdown(f"#### {step_icon} {current_step['name'].replace('_', ' ').title()}")
                    
                    if current_step['status'] == 'running':
                        step_progress.progress(current_step['progress_percentage'] / 100)
                        step_details.info(f"🔄 {current_step['description']}")
                    elif current_step['status'] == 'completed':
                        step_progress.progress(1.0)
                        duration = current_step.get('duration', 0)
                        step_details.success(f"✅ Completed in {duration:.1f}s")
                    elif current_step['status'] == 'failed':
                        step_progress.progress(0.0)
                        step_details.error(f"❌ Failed")
                
                # Update agent activities
                agent_activities = progress_data.get('agent_activities', {})
                if agent_activities:
                    agent_status_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
                    for agent_name, activity in agent_activities.items():
                        status_color = {
                            'active': '#28a745',
                            'completed': '#17a2b8',
                            'failed': '#dc3545'
                        }.get(activity['status'], '#6c757d')
                        
                        agent_status_html += f"""
                        <div style='background: {status_color}; color: white; padding: 8px 12px; 
                                   border-radius: 20px; font-size: 12px; font-weight: bold;'>
                            🤖 {agent_name.replace('_', ' ').title()}: {activity['status'].title()}
                        </div>
                        """
                    agent_status_html += "</div>"
                    agent_status.markdown(agent_status_html, unsafe_allow_html=True)
                
                # Update live logs
                recent_logs = progress_data.get('logs', [])
                if recent_logs:
                    logs_html = "<div style='background: #f8f9fa; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;'>"
                    for log in recent_logs[-10:]:  # Show last 10 logs
                        timestamp = log['timestamp'][:19].replace('T', ' ')
                        level_color = {
                            'info': '#17a2b8',
                            'success': '#28a745',
                            'warning': '#ffc107',
                            'error': '#dc3545'
                        }.get(log['level'], '#6c757d')
                        
                        agent_name = log.get('agent_name', 'System')
                        logs_html += f"""
                        <div style='margin-bottom: 5px; font-size: 12px;'>
                            <span style='color: #6c757d;'>[{timestamp}]</span>
                            <span style='color: {level_color}; font-weight: bold;'>{agent_name}:</span>
                            <span>{log['message']}</span>
                        </div>
                        """
                    logs_html += "</div>"
                    logs_display.markdown(logs_html, unsafe_allow_html=True)
                
                # Update detailed steps
                steps = progress_data.get('steps', [])
                if steps:
                    steps_html = "<div style='display: flex; flex-direction: column; gap: 10px;'>"
                    for i, step in enumerate(steps):
                        status_icon = get_status_icon(step['status'])
                        progress_width = step.get('progress_percentage', 0)
                        
                        # Step container
                        border_color = {
                            'pending': '#e9ecef',
                            'running': '#007bff',
                            'completed': '#28a745',
                            'failed': '#dc3545'
                        }.get(step['status'], '#e9ecef')
                        
                        steps_html += f"""
                        <div style='border: 2px solid {border_color}; border-radius: 8px; padding: 12px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                                <span style='font-weight: bold;'>{status_icon} {step['name'].replace('_', ' ').title()}</span>
                                <span style='font-size: 12px; color: #6c757d;'>
                                    {step.get('duration', 0):.1f}s
                                </span>
                            </div>
                            <div style='font-size: 14px; color: #6c757d; margin-bottom: 8px;'>
                                {step['description']}
                            </div>
                            <div style='background: #e9ecef; border-radius: 10px; height: 6px; overflow: hidden;'>
                                <div style='background: {border_color}; height: 100%; width: {progress_width}%; transition: width 0.3s ease;'></div>
                            </div>
                        </div>
                        """
                    steps_html += "</div>"
                    steps_display.markdown(steps_html, unsafe_allow_html=True)
                
            except Exception as e:
                # Don't let display errors break the generation
                pass
        
        # Run the pipeline with periodic updates
        placeholder = st.empty()
        
        # Start the pipeline in a way that allows for updates
        with st.spinner("Initializing multi-agent pipeline..."):
            # Initialize progress display
            update_progress_display()
            
            # Run pipeline
            results = pipeline.run_pipeline(user_input, project_name)
            
            # Final update
            time.sleep(0.5)  # Brief pause to show completion
            update_progress_display()
            
            # Success message
            st.success("🎉 **Application generated successfully!**")
            
            # Display results
            display_results(results)
    
    except Exception as e:
        st.error(f"❌ **Generation failed:** {str(e)}")
        logger.error(f"Pipeline failed: {str(e)}")
        
        # Show final progress state
        try:
            progress_data = pipeline.get_pipeline_status()['current_progress']
            st.json(progress_data)
        except:
            pass
    
    finally:
        # Reset generation state
        st.session_state.generation_active = False


def get_status_icon(status: str) -> str:
    """Get appropriate icon for status."""
    icons = {
        'pending': '⏳',
        'running': '🔄',
        'completed': '✅',
        'failed': '❌'
    }
    return icons.get(status, '❓')

def display_results(results: Dict[str, Any]):
    """Display the generated application results."""
    
    st.success("🎉 Your application has been generated successfully!")
    
    # Project metadata
    with st.expander("📊 Project Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Project Name", results['project_name'])
        
        with col2:
            execution_time = results['pipeline_metadata']['execution_time_seconds']
            st.metric("Generation Time", f"{execution_time:.1f}s")
        
        with col3:
            progress = results['progress']['progress_percentage']
            st.metric("Completion", f"{progress:.0f}%")
    
    # Tabbed interface for results
    tabs = st.tabs([
        "📋 Requirements", "💻 Code", "📚 Documentation", 
        "🧪 Tests", "🚀 Deployment", "🎨 UI", "📄 Full Results"
    ])
    
    with tabs[0]:  # Requirements
        st.subheader("📋 Analyzed Requirements")
        if 'requirements' in results:
            st.json(results['requirements'])
        else:
            st.warning("Requirements not available")
    
    with tabs[1]:  # Code
        st.subheader("💻 Generated Code")
        if 'code' in results and 'final_code' in results['code']:
            st.code(results['code']['final_code'], language='python')
            
            # Download button
            st.download_button(
                label="📥 Download main.py",
                data=results['code']['final_code'],
                file_name=f"{results['project_name']}_main.py",
                mime="text/plain"
            )
        else:
            st.warning("Code not available")
    
    with tabs[2]:  # Documentation
        st.subheader("📚 Documentation")
        if 'documentation' in results and 'readme' in results['documentation']:
            st.markdown(results['documentation']['readme'])
            
            # Download button
            st.download_button(
                label="📥 Download README.md",
                data=results['documentation']['readme'],
                file_name=f"{results['project_name']}_README.md",
                mime="text/plain"
            )
        else:
            st.warning("Documentation not available")
    
    with tabs[3]:  # Tests
        st.subheader("🧪 Test Cases")
        if 'tests' in results and 'test_code' in results['tests']:
            st.code(results['tests']['test_code'], language='python')
            
            # Download button
            st.download_button(
                label="📥 Download test_main.py",
                data=results['tests']['test_code'],
                file_name=f"{results['project_name']}_test_main.py",
                mime="text/plain"
            )
        else:
            st.warning("Tests not available")
    
    with tabs[4]:  # Deployment
        st.subheader("🚀 Deployment Configuration")
        if 'deployment' in results and 'deployment_configs' in results['deployment']:
            st.markdown(results['deployment']['deployment_configs'])
            
            # Download button
            st.download_button(
                label="📥 Download deployment.md",
                data=results['deployment']['deployment_configs'],
                file_name=f"{results['project_name']}_deployment.md",
                mime="text/plain"
            )
        else:
            st.warning("Deployment configuration not available")
    
    with tabs[5]:  # UI
        st.subheader("🎨 Streamlit UI")
        if 'ui' in results and 'streamlit_app' in results['ui']:
            st.code(results['ui']['streamlit_app'], language='python')
            
            # Download button
            st.download_button(
                label="📥 Download streamlit_app.py",
                data=results['ui']['streamlit_app'],
                file_name=f"{results['project_name']}_streamlit_app.py",
                mime="text/plain"
            )
        else:
            st.warning("UI code not available")
    
    with tabs[6]:  # Full Results
        st.subheader("📄 Complete Results (JSON)")
        st.json(results)
        
        # Download full results
        st.download_button(
            label="📥 Download Full Results (JSON)",
            data=json.dumps(results, indent=2),
            file_name=f"{results['project_name']}_full_results.json",
            mime="application/json"
        )

def show_pipeline_status():
    """Show current pipeline status and progress."""
    
    st.header("📊 Pipeline Status")
    
    try:
        status = pipeline.get_pipeline_status()
        
        # Current progress
        st.subheader("Current Progress")
        progress = status['current_progress']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Steps", progress['total_steps'])
        
        with col2:
            st.metric("Completed", progress['completed_steps'])
        
        with col3:
            st.metric("Failed", progress['failed_steps'])
        
        with col4:
            st.metric("Progress", f"{progress['progress_percentage']:.1f}%")
        
        # Progress bar
        if progress['total_steps'] > 0:
            st.progress(progress['progress_percentage'] / 100)
        
        # Step details
        if progress['steps']:
            st.subheader("Step Details")
            for i, step in enumerate(progress['steps']):
                status_icon = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(step['status'], '❓')
                
                st.write(f"{status_icon} **{step['name']}**: {step['description']}")
                if step['duration']:
                    st.write(f"   Duration: {step['duration']:.2f}s")
        
        # Statistics
        st.subheader("Pipeline Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Runs", status['total_runs'])
        
        with col2:
            st.metric("Successful", status['successful_runs'])
        
        with col3:
            st.metric("Failed", status['failed_runs'])
        
    except Exception as e:
        st.error(f"Failed to load pipeline status: {str(e)}")

def show_agent_info():
    """Show information about available agents."""
    
    st.header("🤖 Agent Information")
    
    try:
        agent_info = pipeline.get_agent_info()
        
        # Pipeline overview
        st.subheader("Pipeline Overview")
        st.markdown("The multi-agent framework follows these steps:")
        
        for i, step in enumerate(agent_info['pipeline_steps'], 1):
            st.write(f"{i}. **{step}**")
        
        # Agent descriptions
        st.subheader("Agent Descriptions")
        
        for agent_key, description in agent_info['agent_descriptions'].items():
            with st.expander(f"🤖 {agent_key.replace('_', ' ').title()}"):
                st.write(description)
                
                # Add more details based on agent type
                if 'requirement' in agent_key:
                    st.markdown("""
                    **Capabilities:**
                    - Natural language processing
                    - Requirement extraction and structuring
                    - Ambiguity detection and clarification
                    - JSON output formatting
                    """)
                elif 'coder' in agent_key:
                    st.markdown("""
                    **Capabilities:**
                    - Python code generation
                    - Best practices implementation
                    - Type hints and documentation
                    - Error handling and logging
                    """)
                elif 'reviewer' in agent_key:
                    st.markdown("""
                    **Capabilities:**
                    - Code quality analysis
                    - Security vulnerability detection
                    - Performance optimization
                    - Best practices validation
                    """)
        
        # Available agents
        st.subheader("Available Agents")
        st.write("Currently loaded agents:")
        for agent in agent_info['available_agents']:
            st.write(f"✅ {agent}")
            
    except Exception as e:
        st.error(f"Failed to load agent information: {str(e)}")

def show_project_history():
    """Show project generation history."""
    
    st.header("📚 Project History")
    
    try:
        status = pipeline.get_pipeline_status()
        history = status['pipeline_history']
        
        if not history:
            st.info("No projects generated yet. Start by creating your first application!")
            return
        
        # Summary statistics
        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Projects", len(history))
        
        with col2:
            successful = sum(1 for h in history if h['success'])
            st.metric("Successful", successful)
        
        with col3:
            avg_time = sum(h['execution_time'] for h in history) / len(history)
            st.metric("Avg. Time", f"{avg_time:.1f}s")
        
        # Project list
        st.subheader("Project List")
        
        for i, project in enumerate(reversed(history), 1):
            with st.expander(f"Project {i}: {project['project_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Timestamp:** {project['timestamp']}")
                    st.write(f"**Success:** {'✅' if project['success'] else '❌'}")
                    st.write(f"**Execution Time:** {project['execution_time']:.2f}s")
                
                with col2:
                    st.write("**User Input:**")
                    st.write(project['user_input'][:200] + "..." if len(project['user_input']) > 200 else project['user_input'])
                
                if not project['success'] and 'error' in project:
                    st.error(f"Error: {project['error']}")
                    
    except Exception as e:
        st.error(f"Failed to load project history: {str(e)}")

if __name__ == "__main__":
    main()
