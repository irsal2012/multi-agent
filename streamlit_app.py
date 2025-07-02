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
            ["Code Generator", "Agent Information", "Project History"]
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
            
            # Removed duplicate step details - now only shown in main pipeline steps section
            
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
    """Generate application using the multi-agent pipeline."""
    
    # Initialize session state for progress tracking
    if 'generation_active' not in st.session_state:
        st.session_state.generation_active = False
    
    if st.session_state.generation_active:
        st.warning("⚠️ Generation already in progress. Please wait for completion.")
        return
    
    # Set generation as active
    st.session_state.generation_active = True
    
    try:
        # Create progress interface
        st.subheader("🚀 Generation in Progress")
        
        # Show initial progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Show pipeline steps
        st.markdown("### 📋 Pipeline Steps")
        step_placeholders = []
        for i, step_name in enumerate([
            "Requirements Analysis",
            "Code Generation", 
            "Code Review",
            "Documentation",
            "Test Generation",
            "Deployment Config",
            "UI Generation"
        ]):
            placeholder = st.empty()
            placeholder.info(f"⏳ **{i+1}. {step_name}** - Waiting")
            step_placeholders.append(placeholder)
        
        # Run the pipeline with progress updates
        with st.spinner("Running multi-agent pipeline..."):
            try:
                # Update initial status
                status_text.info("🚀 **Starting pipeline execution...**")
                progress_bar.progress(0.05)
                
                # Run the pipeline
                results = pipeline.run_pipeline(user_input, project_name)
                
                # Update final progress
                progress_bar.progress(1.0)
                status_text.success("✅ **Generation Completed Successfully!**")
                
                # Update all steps to completed
                for i, placeholder in enumerate(step_placeholders):
                    step_name = [
                        "Requirements Analysis",
                        "Code Generation", 
                        "Code Review",
                        "Documentation",
                        "Test Generation",
                        "Deployment Config",
                        "UI Generation"
                    ][i]
                    placeholder.success(f"✅ **{i+1}. {step_name}** - Completed")
                
                # Display results
                st.success("🎉 **Application generated successfully!**")
                display_results(results)
                
            except Exception as e:
                # Update progress to show failure
                progress_bar.progress(0.5)
                status_text.error(f"❌ **Generation Failed:** {str(e)}")
                
                # Show error details
                st.error(f"Pipeline execution failed: {str(e)}")
                
                # Show debug information
                with st.expander("🔍 Debug Information"):
                    st.write("**Error Details:**")
                    st.code(str(e))
                    
                    try:
                        pipeline_status = pipeline.get_pipeline_status()
                        st.write("**Pipeline Status:**")
                        st.json(pipeline_status)
                    except Exception as debug_e:
                        st.write(f"Could not retrieve pipeline status: {str(debug_e)}")
                
                raise
    
    except Exception as e:
        st.error(f"❌ **Generation failed:** {str(e)}")
        logger.error(f"Pipeline failed: {str(e)}")
    
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
