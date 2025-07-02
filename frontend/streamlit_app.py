"""
Clean Streamlit frontend that communicates with FastAPI backend.
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from client.api_client import APIClient

# Configure page
st.set_page_config(
    page_title="Multi-Agent Code Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
@st.cache_resource
def get_api_client():
    """Get API client instance."""
    return APIClient()

api_client = get_api_client()

def check_backend_connection():
    """Check if backend is available."""
    if not api_client.health_check():
        st.error("❌ **Backend not available**")
        st.info("Please ensure the FastAPI backend is running on http://localhost:8000")
        st.code("cd backend && python main.py")
        st.stop()

def main():
    """Main Streamlit application."""
    
    # Check backend connection
    check_backend_connection()
    
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
            ["Code Generator", "Agent Information", "Project History"]
        )
        
        st.markdown("---")
        st.markdown("### Backend Status")
        if api_client.health_check():
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Disconnected")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This framework uses a FastAPI backend with AutoGen agents,
        each specialized in different aspects of software development.
        """)
    
    # Route to different pages
    if page == "Code Generator":
        show_code_generator()
    elif page == "Agent Information":
        show_agent_info()
    elif page == "Project History":
        show_project_history()

def show_code_generator():
    """Main code generation interface."""
    
    st.header("🚀 Generate Your Application")
    
    # Pipeline Status Section
    with st.expander("📊 Pipeline Status", expanded=False):
        try:
            status = api_client.get_pipeline_status()
            if status:
                # Current progress
                st.subheader("Current Progress")
                progress = status.get('current_progress', {})
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Steps", progress.get('total_steps', 0))
                
                with col2:
                    st.metric("Completed", progress.get('completed_steps', 0))
                
                with col3:
                    st.metric("Failed", progress.get('failed_steps', 0))
                
                with col4:
                    st.metric("Progress", f"{progress.get('progress_percentage', 0):.1f}%")
                
                # Progress bar
                if progress.get('total_steps', 0) > 0:
                    st.progress(progress.get('progress_percentage', 0) / 100)
                
                # Statistics
                st.subheader("Pipeline Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Runs", status.get('total_runs', 0))
                
                with col2:
                    st.metric("Successful", status.get('successful_runs', 0))
                
                with col3:
                    st.metric("Failed", status.get('failed_runs', 0))
            else:
                st.warning("Could not load pipeline status")
                
        except Exception as e:
            st.error(f"Failed to load pipeline status: {str(e)}")
    
    # Quick Examples
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
            validation = api_client.validate_input(user_input)
            
            if validation and validation.get('warnings'):
                for warning in validation['warnings']:
                    st.warning(f"⚠️ {warning}")
            
            if validation and validation.get('suggestions'):
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
    """Generate application using the backend API."""
    
    try:
        # Start generation
        response = api_client.generate_code(user_input, project_name)
        
        if not response:
            st.error("Failed to start code generation")
            return
        
        project_id = response.get('project_id')
        if not project_id:
            st.error("No project ID received from backend")
            return
        
        st.success(f"🎉 Generation started! Project ID: {project_id}")
        
        # Store project ID in session state
        st.session_state.current_project_id = project_id
        
        # Show progress tracking
        show_generation_progress(project_id)
        
    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")

def show_generation_progress(project_id: str):
    """Show real-time progress for a generation."""
    
    st.subheader("🚀 Generation in Progress")
    
    # Create progress interface
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Show pipeline steps
    st.markdown("### 📋 Pipeline Steps")
    step_placeholders = []
    step_names = [
        "Requirements Analysis",
        "Code Generation", 
        "Code Review",
        "Documentation",
        "Test Generation",
        "Deployment Config",
        "UI Generation"
    ]
    
    for i, step_name in enumerate(step_names):
        placeholder = st.empty()
        placeholder.info(f"⏳ **{i+1}. {step_name}** - Waiting")
        step_placeholders.append(placeholder)
    
    # Poll for progress updates
    max_polls = 300  # 5 minutes with 1-second intervals
    poll_count = 0
    
    while poll_count < max_polls:
        try:
            progress = api_client.get_project_progress(project_id)
            
            if progress:
                # Update main progress bar
                progress_percentage = progress.get('progress_percentage', 0)
                progress_bar.progress(progress_percentage / 100)
                
                # Update status text
                if progress.get('is_completed'):
                    status_text.success("✅ **Generation Completed Successfully!**")
                    break
                elif progress.get('has_failures'):
                    status_text.error("❌ **Generation Failed**")
                    break
                elif progress.get('is_running'):
                    current_step_info = progress.get('current_step_info')
                    if current_step_info:
                        status_text.info(f"🔄 **{current_step_info.get('description', 'Processing...')}**")
                
                # Update individual step displays
                steps = progress.get('steps', [])
                for i, step in enumerate(steps):
                    if i < len(step_placeholders):
                        step_name = step_names[i] if i < len(step_names) else f"Step {i+1}"
                        status = step.get('status', 'pending')
                        
                        if status == 'running':
                            step_placeholders[i].info(f"🔄 **{i+1}. {step_name}** - Running")
                        elif status == 'completed':
                            step_placeholders[i].success(f"✅ **{i+1}. {step_name}** - Completed")
                        elif status == 'failed':
                            step_placeholders[i].error(f"❌ **{i+1}. {step_name}** - Failed")
                        else:
                            step_placeholders[i].info(f"⏳ **{i+1}. {step_name}** - Waiting")
            
            time.sleep(1)
            poll_count += 1
            
        except Exception as e:
            st.error(f"Error polling progress: {str(e)}")
            break
    
    # Check final result
    try:
        result = api_client.get_project_result(project_id)
        if result:
            display_results(result)
        else:
            st.warning("Generation completed but no results available")
    except Exception as e:
        st.error(f"Failed to get final results: {str(e)}")

def display_results(results: Dict[str, Any]):
    """Display the generated application results."""
    
    st.success("🎉 Your application has been generated successfully!")
    
    # Project metadata
    with st.expander("📊 Project Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Project Name", results.get('project_name', 'Unknown'))
        
        with col2:
            metadata = results.get('pipeline_metadata', {})
            execution_time = metadata.get('execution_time_seconds', 0)
            st.metric("Generation Time", f"{execution_time:.1f}s")
        
        with col3:
            progress = results.get('progress', {})
            progress_pct = progress.get('progress_percentage', 0)
            st.metric("Completion", f"{progress_pct:.0f}%")
    
    # Tabbed interface for results
    tabs = st.tabs([
        "📋 Requirements", "💻 Code", "📚 Documentation", 
        "🧪 Tests", "🚀 Deployment", "🎨 UI", "📄 Full Results"
    ])
    
    with tabs[0]:  # Requirements
        st.subheader("📋 Analyzed Requirements")
        requirements = results.get('requirements')
        if requirements:
            st.json(requirements)
        else:
            st.warning("Requirements not available")
    
    with tabs[1]:  # Code
        st.subheader("💻 Generated Code")
        code = results.get('code', {})
        final_code = code.get('final_code')
        if final_code:
            st.code(final_code, language='python')
            
            # Download button
            st.download_button(
                label="📥 Download main.py",
                data=final_code,
                file_name=f"{results.get('project_name', 'project')}_main.py",
                mime="text/plain"
            )
        else:
            st.warning("Code not available")
    
    with tabs[2]:  # Documentation
        st.subheader("📚 Documentation")
        documentation = results.get('documentation', {})
        readme = documentation.get('readme')
        if readme:
            st.markdown(readme)
            
            # Download button
            st.download_button(
                label="📥 Download README.md",
                data=readme,
                file_name=f"{results.get('project_name', 'project')}_README.md",
                mime="text/plain"
            )
        else:
            st.warning("Documentation not available")
    
    with tabs[3]:  # Tests
        st.subheader("🧪 Test Cases")
        tests = results.get('tests', {})
        test_code = tests.get('test_code')
        if test_code:
            st.code(test_code, language='python')
            
            # Download button
            st.download_button(
                label="📥 Download test_main.py",
                data=test_code,
                file_name=f"{results.get('project_name', 'project')}_test_main.py",
                mime="text/plain"
            )
        else:
            st.warning("Tests not available")
    
    with tabs[4]:  # Deployment
        st.subheader("🚀 Deployment Configuration")
        deployment = results.get('deployment', {})
        deployment_configs = deployment.get('deployment_configs')
        if deployment_configs:
            st.markdown(deployment_configs)
            
            # Download button
            st.download_button(
                label="📥 Download deployment.md",
                data=deployment_configs,
                file_name=f"{results.get('project_name', 'project')}_deployment.md",
                mime="text/plain"
            )
        else:
            st.warning("Deployment configuration not available")
    
    with tabs[5]:  # UI
        st.subheader("🎨 Streamlit UI")
        ui = results.get('ui', {})
        streamlit_app = ui.get('streamlit_app')
        if streamlit_app:
            st.code(streamlit_app, language='python')
            
            # Download button
            st.download_button(
                label="📥 Download streamlit_app.py",
                data=streamlit_app,
                file_name=f"{results.get('project_name', 'project')}_streamlit_app.py",
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
            data=json.dumps(results, indent=2, default=str),
            file_name=f"{results.get('project_name', 'project')}_full_results.json",
            mime="application/json"
        )

def show_agent_info():
    """Show information about available agents."""
    
    st.header("🤖 Agent Information")
    
    try:
        agent_info = api_client.get_agents_info()
        
        if not agent_info:
            st.error("Failed to load agent information")
            return
        
        # Pipeline overview
        st.subheader("Pipeline Overview")
        st.markdown("The multi-agent framework follows these steps:")
        
        pipeline_steps = agent_info.get('pipeline_steps', [])
        for i, step in enumerate(pipeline_steps, 1):
            st.write(f"{i}. **{step}**")
        
        # Agent descriptions
        st.subheader("Agent Descriptions")
        
        agents_info = agent_info.get('agents_info', [])
        for agent in agents_info:
            with st.expander(f"🤖 {agent.get('name', 'Unknown Agent')}"):
                st.write(agent.get('description', 'No description available'))
                
                capabilities = agent.get('capabilities', [])
                if capabilities:
                    st.markdown("**Capabilities:**")
                    for capability in capabilities:
                        st.write(f"- {capability}")
        
        # Available agents
        st.subheader("Available Agents")
        available_agents = agent_info.get('available_agents', [])
        st.write("Currently loaded agents:")
        for agent in available_agents:
            st.write(f"✅ {agent}")
            
    except Exception as e:
        st.error(f"Failed to load agent information: {str(e)}")

def show_project_history():
    """Show project generation history."""
    
    st.header("📚 Project History")
    
    try:
        # Get project statistics
        stats = api_client.get_project_statistics()
        
        if stats:
            # Summary statistics
            st.subheader("Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Projects", stats.get('total_projects', 0))
            
            with col2:
                st.metric("Successful", stats.get('successful_projects', 0))
            
            with col3:
                st.metric("Failed", stats.get('failed_projects', 0))
            
            with col4:
                success_rate = stats.get('success_rate', 0)
                st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Get project history
        history = api_client.get_project_history(limit=20)
        
        if not history or not history.get('projects'):
            st.info("No projects generated yet. Start by creating your first application!")
            return
        
        # Project list
        st.subheader("Recent Projects")
        
        projects = history.get('projects', [])
        for i, project in enumerate(projects, 1):
            with st.expander(f"Project {i}: {project.get('project_name', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    timestamp = project.get('timestamp', '')
                    if isinstance(timestamp, str):
                        try:
                            # Parse ISO timestamp
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            formatted_time = timestamp
                    else:
                        formatted_time = str(timestamp)
                    
                    st.write(f"**Timestamp:** {formatted_time}")
                    st.write(f"**Success:** {'✅' if project.get('success') else '❌'}")
                    st.write(f"**Execution Time:** {project.get('execution_time', 0):.2f}s")
                
                with col2:
                    st.write("**User Input:**")
                    user_input = project.get('user_input', '')
                    display_input = user_input[:200] + "..." if len(user_input) > 200 else user_input
                    st.write(display_input)
                
                error = project.get('error')
                if not project.get('success') and error:
                    st.error(f"Error: {error}")
                    
    except Exception as e:
        st.error(f"Failed to load project history: {str(e)}")

if __name__ == "__main__":
    main()
