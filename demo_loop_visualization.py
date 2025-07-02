"""
Standalone demo of the Loop Visualization system.
Run this to see the real-time back-and-forth between code generation and review.
"""

import streamlit as st
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loop_visualizer import create_demo_loop_visualizer

# Configure page
st.set_page_config(
    page_title="Loop Visualization Demo",
    page_icon="🔄",
    layout="wide"
)

def main():
    """Main demo application."""
    
    st.title("🔄 Code Generation ↔ Review Loop Demo")
    
    st.markdown("""
    This demo shows the **real-time back-and-forth visualization** between code generation and review processes.
    
    ## Features Demonstrated:
    - **Live Progress Tracking**: See both generation and review progress in real-time
    - **Iteration Counter**: Track multiple improvement cycles
    - **Feedback Exchange**: View actual feedback flowing between processes
    - **Convergence Metrics**: Monitor quality improvement over iterations
    - **Interactive Charts**: Plotly visualizations showing progress trends
    - **Loop History**: Complete record of all iterations and improvements
    
    ## How It Works:
    1. **Generation Phase**: AI agent generates or improves code based on requirements/feedback
    2. **Review Phase**: AI agent reviews code quality, security, and best practices
    3. **Feedback Loop**: Review feedback is passed back to generation for improvements
    4. **Convergence**: Process continues until quality threshold is met or max iterations reached
    
    Click "Start Demo Loop" below to see the visualization in action!
    """)
    
    st.markdown("---")
    
    # Run the demo
    create_demo_loop_visualizer()
    
    st.markdown("---")
    
    # Additional information
    with st.expander("🔧 Technical Details", expanded=False):
        st.markdown("""
        ### Implementation Details
        
        **Loop Progress Tracker**:
        - Tracks multiple iterations with detailed progress for each phase
        - Monitors convergence scores and quality metrics
        - Stores feedback history and timing information
        
        **Visualization Components**:
        - Real-time progress bars for generation and review
        - Interactive Plotly charts showing trends across iterations
        - Live feedback stream with categorized messages
        - Iteration history with expandable details
        
        **Integration Points**:
        - Seamlessly integrates with existing AutoGen agent pipeline
        - Provides hooks for real-time UI updates
        - Maintains backward compatibility with linear progress tracking
        
        ### Configuration Options
        - **Convergence Threshold**: Quality score needed to complete (default: 85%)
        - **Max Iterations**: Maximum number of improvement cycles (default: 3)
        - **Progress Update Frequency**: How often UI refreshes during demo
        """)
    
    with st.expander("🎯 Use Cases", expanded=False):
        st.markdown("""
        ### When to Use Loop Visualization
        
        **Code Quality Improvement**:
        - Show iterative refinement of generated code
        - Track security and performance improvements
        - Demonstrate best practices adoption
        
        **Educational Purposes**:
        - Teach iterative development processes
        - Show AI collaboration in action
        - Demonstrate quality assurance workflows
        
        **Process Monitoring**:
        - Monitor AI agent performance over time
        - Identify common feedback patterns
        - Optimize convergence thresholds
        
        **User Engagement**:
        - Make long-running processes more transparent
        - Provide interactive feedback during generation
        - Build confidence in AI-generated code quality
        """)

if __name__ == "__main__":
    main()
