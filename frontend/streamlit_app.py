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

# Add cache clearing button in sidebar for debugging
if st.sidebar.button("🔄 Clear Cache", help="Clear API client cache if experiencing issues"):
    st.cache_resource.clear()
    st.rerun()

api_client = get_api_client()

def check_backend_connection():
    """Check if backend is available with detailed diagnostics."""
    with st.spinner("Checking backend connection..."):
        # Try to get detailed health status, fallback to basic health check
        try:
            health_status = api_client.get_detailed_health_status()
        except AttributeError:
            # Fallback if method doesn't exist (cache issue)
            st.warning("Using fallback health check method")
            if api_client.health_check():
                health_status = {"status": "healthy", "ready": True}
            else:
                health_status = {"status": "unreachable", "ready": False, "error": "Connection failed"}
        
        if health_status.get('ready', False):
            # Backend is healthy and ready
            return True
        
        # Backend is not ready or unreachable
        st.error("❌ **Backend Connection Issue**")
        
        status = health_status.get('status', 'unknown')
        error = health_status.get('error', 'Unknown error')
        
        if status == 'unreachable':
            st.error(f"**Cannot reach backend:** {error}")
            st.info("**Troubleshooting Steps:**")
            st.markdown("""
            1. **Check if backend is running:**
               ```bash
               cd backend && python main.py
               ```
            2. **Verify backend is accessible:**
               - Open http://localhost:8000 in your browser
               - You should see the API welcome message
            3. **Check for port conflicts:**
               - Make sure no other service is using port 8000
            4. **Firewall/Network issues:**
               - Ensure localhost connections are allowed
            """)
            
        elif status == 'unhealthy':
            st.error(f"**Backend is running but unhealthy:** {error}")
            st.info("**Backend Status Details:**")
            
            # Show service status if available
            services = health_status.get('services', {})
            if services:
                for service_name, service_status in services.items():
                    if 'error' in str(service_status):
                        st.error(f"❌ {service_name}: {service_status}")
                    else:
                        st.success(f"✅ {service_name}: {service_status}")
            
            st.info("**Possible Solutions:**")
            st.markdown("""
            - Restart the backend server
            - Check backend logs for detailed error messages
            - Ensure all dependencies are installed
            """)
            
        else:
            st.warning(f"**Backend status unclear:** {status}")
            if error:
                st.error(f"Error details: {error}")
        
        # Add connection test button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Retry Connection", key="retry_connection"):
                st.rerun()
        
        with col2:
            if st.button("🔍 Show Advanced Diagnostics", key="show_diagnostics"):
                st.session_state.show_diagnostics = True
        
        # Show advanced diagnostics if requested
        if st.session_state.get('show_diagnostics', False):
            st.subheader("🔍 Advanced Diagnostics")
            
            # Test basic connectivity
            st.write("**Testing connectivity to backend...**")
            try:
                import requests
                response = requests.get("http://localhost:8000", timeout=5)
                st.success(f"✅ Basic HTTP connection successful (Status: {response.status_code})")
            except Exception as e:
                st.error(f"❌ Basic HTTP connection failed: {str(e)}")
            
            # Show full health status
            st.write("**Full Health Status Response:**")
            st.json(health_status)
            
            # Show backend URL being used
            st.write(f"**Backend URL:** {api_client.base_url}")
            
            # Connection settings
            st.write("**Connection Settings:**")
            st.code(f"""
Base URL: {api_client.base_url}
Connect Timeout: 10.0 seconds
Read Timeout: 30.0 seconds
            """)
        
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
    
    # Progress Tracking Test Section
    with st.expander("🧪 Test Progress Tracking", expanded=False):
        st.markdown("Use this section to test the progress tracking functionality.")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            test_project_id = st.text_input(
                "Test Project ID", 
                value="test-123",
                help="Enter a project ID to test progress tracking"
            )
        
        with col2:
            if st.button("🧪 Test Progress", use_container_width=True):
                if test_project_id:
                    with st.spinner("Creating test progress data..."):
                        test_result = api_client.test_progress_tracking(test_project_id)
                        if test_result:
                            st.success("✅ Test progress created successfully!")
                            st.json(test_result)
                            
                            # Show the test progress
                            st.markdown("### Test Progress Display")
                            show_generation_progress(test_project_id)
                        else:
                            st.error("❌ Failed to create test progress")
                else:
                    st.error("Please enter a test project ID")
    
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
    debug_info = st.empty()
    
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
    
    # Add cancel button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("❌ Cancel", key="cancel_generation"):
            if api_client.cancel_project(project_id):
                st.warning("Generation cancelled")
                return
            else:
                st.error("Failed to cancel generation")
    
    # Poll for progress updates with improved error handling
    max_polls = 300  # 5 minutes with 1-second intervals
    poll_count = 0
    consecutive_errors = 0
    last_progress_percentage = 0
    
    while poll_count < max_polls:
        try:
            progress = api_client.get_project_progress(project_id)
            
            if progress:
                consecutive_errors = 0  # Reset error counter on success
                
                # Update main progress bar
                progress_percentage = progress.get('progress_percentage', 0)
                if progress_percentage > last_progress_percentage:
                    last_progress_percentage = progress_percentage
                progress_bar.progress(progress_percentage / 100)
                
                # Show debug info in expander
                with debug_info.expander("🔍 Debug Info", expanded=False):
                    st.json({
                        'progress_percentage': progress_percentage,
                        'is_running': progress.get('is_running', False),
                        'is_completed': progress.get('is_completed', False),
                        'has_failures': progress.get('has_failures', False),
                        'completed_steps': progress.get('completed_steps', 0),
                        'total_steps': progress.get('total_steps', 0),
                        'poll_count': poll_count
                    })
                
                # Update status text
                if progress.get('is_completed'):
                    status_text.success("✅ **Generation Completed Successfully!**")
                    break
                elif progress.get('has_failures'):
                    status_text.error("❌ **Generation Failed**")
                    # Show error details if available
                    logs = progress.get('logs', [])
                    error_logs = [log for log in logs if log.get('level') == 'ERROR']
                    if error_logs:
                        st.error(f"Error details: {error_logs[-1].get('message', 'Unknown error')}")
                    break
                elif progress.get('is_running'):
                    current_step_info = progress.get('current_step_info')
                    if current_step_info:
                        step_desc = current_step_info.get('description', 'Processing...')
                        agent_name = current_step_info.get('agent_name', '')
                        if agent_name:
                            status_text.info(f"🔄 **{step_desc}** (Agent: {agent_name})")
                        else:
                            status_text.info(f"🔄 **{step_desc}**")
                    else:
                        status_text.info(f"🔄 **Processing...** ({progress_percentage:.1f}% complete)")
                else:
                    status_text.info(f"⏳ **Initializing...** ({progress_percentage:.1f}% complete)")
                
                # Update individual step displays
                steps = progress.get('steps', [])
                for i, step in enumerate(steps):
                    if i < len(step_placeholders):
                        step_name = step_names[i] if i < len(step_names) else f"Step {i+1}"
                        status = step.get('status', 'pending')
                        step_progress = step.get('progress_percentage', 0)
                        
                        if status == 'running':
                            step_placeholders[i].info(f"🔄 **{i+1}. {step_name}** - Running ({step_progress:.0f}%)")
                        elif status == 'completed':
                            step_placeholders[i].success(f"✅ **{i+1}. {step_name}** - Completed")
                        elif status == 'failed':
                            step_placeholders[i].error(f"❌ **{i+1}. {step_name}** - Failed")
                        else:
                            step_placeholders[i].info(f"⏳ **{i+1}. {step_name}** - Waiting")
                
                # Update remaining steps as waiting if we have fewer steps than expected
                for i in range(len(steps), len(step_placeholders)):
                    step_name = step_names[i] if i < len(step_names) else f"Step {i+1}"
                    step_placeholders[i].info(f"⏳ **{i+1}. {step_name}** - Waiting")
            
            else:
                consecutive_errors += 1
                if consecutive_errors <= 3:
                    # Don't show warnings for the first few attempts
                    pass
                elif consecutive_errors <= 8:
                    status_text.warning(f"⚠️ Waiting for progress data... (attempt {consecutive_errors})")
                elif consecutive_errors <= 15:
                    status_text.warning(f"⚠️ No progress data received for {consecutive_errors} consecutive attempts. Pipeline may still be initializing...")
                else:
                    status_text.error("❌ Lost connection to backend or pipeline failed to start. Please check if the backend is running.")
                    break
            
            time.sleep(1)
            poll_count += 1
            
        except Exception as e:
            consecutive_errors += 1
            error_msg = str(e)
            
            if consecutive_errors <= 3:
                # Show temporary error message
                status_text.warning(f"⚠️ Connection issue (attempt {consecutive_errors}/3): {error_msg}")
            elif consecutive_errors <= 10:
                # Show persistent warning
                st.warning(f"⚠️ Persistent connection issues. Retrying... (attempt {consecutive_errors})")
            else:
                # Give up after too many errors
                st.error(f"❌ Too many connection errors. Please check your backend connection: {error_msg}")
                break
            
            time.sleep(2)  # Wait longer between retries on error
            poll_count += 1
    
    # Handle timeout
    if poll_count >= max_polls:
        st.warning("⏰ Progress polling timed out. The generation may still be running in the background.")
    
    # Check final result
    try:
        result = api_client.get_project_result(project_id)
        if result:
            display_results(result)
        else:
            # Try to get project status to see what happened
            try:
                final_progress = api_client.get_project_progress(project_id)
                if final_progress and final_progress.get('is_completed'):
                    st.warning("Generation completed but results are not yet available. Please try refreshing the page.")
                elif final_progress and final_progress.get('has_failures'):
                    st.error("Generation failed. Check the logs above for details.")
                else:
                    st.info("Generation may still be in progress. Please wait a moment and refresh the page.")
            except:
                st.warning("Generation status unclear. Please check the Project History page for updates.")
    except Exception as e:
        st.error(f"Failed to get final results: {str(e)}")
        st.info("You can check the Project History page to see if your generation completed successfully.")

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
