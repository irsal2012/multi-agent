"""
Real-time Loop Visualizer for Code Generation and Review Process.
Shows the back-and-forth between generation and review with live updates.
"""

import streamlit as st
import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.loop_progress_tracker import LoopProgressTracker, LoopState

class LoopVisualizer:
    """Streamlit component for visualizing generation-review loops."""
    
    def __init__(self):
        self.tracker: Optional[LoopProgressTracker] = None
        
    def create_loop_interface(self, tracker: LoopProgressTracker) -> None:
        """Create the main loop visualization interface."""
        self.tracker = tracker
        
        # Main header
        st.markdown("## 🔄 Code Generation ↔ Review Loop")
        
        # Get current status
        status = tracker.get_current_status()
        
        # Loop overview metrics
        self._show_loop_metrics(status)
        
        # Current iteration display
        if status['current_iteration']:
            self._show_current_iteration(status)
        
        # Progress visualization
        self._show_progress_visualization(status)
        
        # Feedback stream
        self._show_feedback_stream(tracker)
        
        # Iteration history
        self._show_iteration_history(tracker)
    
    def _show_loop_metrics(self, status: Dict[str, Any]) -> None:
        """Show high-level loop metrics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Iteration", 
                status['total_iterations'],
                delta=f"Max: {status['max_iterations']}"
            )
        
        with col2:
            convergence = self.tracker.get_convergence_progress() if self.tracker else 0
            st.metric(
                "Convergence", 
                f"{convergence:.1f}%",
                delta=f"Target: {status['convergence_threshold']*100:.0f}%"
            )
        
        with col3:
            duration = status['total_duration']
            st.metric(
                "Total Time", 
                f"{duration:.1f}s"
            )
        
        with col4:
            state_emoji = {
                'idle': '⏸️',
                'generation': '🔧',
                'review': '🔍',
                'converging': '🎯',
                'completed': '✅',
                'failed': '❌'
            }
            st.metric(
                "Status", 
                status['state'].title(),
                delta=state_emoji.get(status['state'], '❓')
            )
    
    def _show_current_iteration(self, status: Dict[str, Any]) -> None:
        """Show current iteration details."""
        current = status['current_iteration']
        
        st.markdown(f"### 🔄 Iteration #{current['number']}")
        
        # Create two columns for generation and review
        col1, col2 = st.columns(2)
        
        with col1:
            self._show_process_card(
                "Code Generation", 
                current['generation_progress'],
                current['generation_status'],
                "🔧",
                status['active_process'] == 'generation'
            )
        
        with col2:
            self._show_process_card(
                "Code Review", 
                current['review_progress'],
                current['review_status'],
                "🔍",
                status['active_process'] == 'review'
            )
        
        # Show feedback flow if available
        if current['latest_feedback']:
            st.markdown("#### 💬 Latest Feedback")
            for feedback in current['latest_feedback']:
                st.info(f"💡 {feedback}")
        
        # Quality metrics
        if current['quality_score'] > 0 or current['convergence_score'] > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Quality Score", f"{current['quality_score']:.1f}")
            with col2:
                st.metric("Convergence Score", f"{current['convergence_score']:.2f}")
    
    def _show_process_card(self, title: str, progress: float, status: str, 
                          icon: str, is_active: bool) -> None:
        """Show a process card for generation or review."""
        
        # Determine card styling based on status and activity
        if is_active:
            border_color = "#1f77b4" if "generation" in title.lower() else "#2ca02c"
            st.markdown(f"""
            <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 15px; margin: 5px;">
                <h4>{icon} {title}</h4>
                <p><strong>Status:</strong> {status.title()}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 5px;">
                <h4>{icon} {title}</h4>
                <p><strong>Status:</strong> {status.title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar
        if status == "running":
            st.progress(progress / 100.0)
            st.caption(f"{progress:.1f}% complete")
        elif status == "completed":
            st.progress(1.0)
            st.success("✅ Completed")
        else:
            st.progress(0.0)
            st.caption("Waiting...")
    
    def _show_progress_visualization(self, status: Dict[str, Any]) -> None:
        """Show interactive progress visualization."""
        st.markdown("### 📊 Progress Visualization")
        
        if not self.tracker or not self.tracker.iterations:
            st.info("No iterations to display yet.")
            return
        
        # Create plotly chart showing iteration progress
        fig = self._create_progress_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_progress_chart(self) -> go.Figure:
        """Create a plotly chart showing loop progress."""
        iterations = self.tracker.get_all_iterations()
        
        if not iterations:
            # Empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Generation vs Review Progress', 'Convergence Score'),
            vertical_spacing=0.1
        )
        
        # Extract data
        iteration_numbers = [it['number'] for it in iterations]
        gen_progress = [it['generation_progress'] for it in iterations]
        review_progress = [it['review_progress'] for it in iterations]
        convergence_scores = [it['convergence_score'] * 100 for it in iterations]
        
        # Add generation progress
        fig.add_trace(
            go.Scatter(
                x=iteration_numbers,
                y=gen_progress,
                mode='lines+markers',
                name='Code Generation',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add review progress
        fig.add_trace(
            go.Scatter(
                x=iteration_numbers,
                y=review_progress,
                mode='lines+markers',
                name='Code Review',
                line=dict(color='#2ca02c', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add convergence score
        fig.add_trace(
            go.Scatter(
                x=iteration_numbers,
                y=convergence_scores,
                mode='lines+markers',
                name='Convergence Score',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        # Add convergence threshold line
        threshold_line = self.tracker.convergence_threshold * 100
        fig.add_hline(
            y=threshold_line,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Target: {threshold_line:.0f}%",
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=500,
            showlegend=True,
            title_text="Real-time Loop Progress"
        )
        
        fig.update_xaxes(title_text="Iteration", row=2, col=1)
        fig.update_yaxes(title_text="Progress (%)", row=1, col=1)
        fig.update_yaxes(title_text="Convergence (%)", row=2, col=1)
        
        return fig
    
    def _show_feedback_stream(self, tracker: LoopProgressTracker) -> None:
        """Show live feedback stream."""
        st.markdown("### 💬 Feedback Stream")
        
        # Get recent logs
        logs = tracker.get_recent_logs(20)
        
        if not logs:
            st.info("No feedback available yet.")
            return
        
        # Create expandable log viewer
        with st.expander("📋 View All Logs", expanded=False):
            for log in reversed(logs):  # Show newest first
                timestamp = datetime.fromisoformat(log['timestamp']).strftime("%H:%M:%S")
                level = log['level']
                source = log['source']
                message = log['message']
                
                # Style based on level
                if level == "error":
                    st.error(f"[{timestamp}] {source}: {message}")
                elif level == "warning":
                    st.warning(f"[{timestamp}] {source}: {message}")
                elif level == "success":
                    st.success(f"[{timestamp}] {source}: {message}")
                else:
                    st.info(f"[{timestamp}] {source}: {message}")
        
        # Show latest feedback prominently
        feedback_logs = [log for log in logs if "Feedback:" in log['message']]
        if feedback_logs:
            st.markdown("#### 🔄 Latest Feedback Exchange")
            for log in feedback_logs[-3:]:  # Show last 3 feedback items
                message = log['message'].replace("Feedback: ", "")
                st.info(f"💡 {message}")
    
    def _show_iteration_history(self, tracker: LoopProgressTracker) -> None:
        """Show history of all iterations."""
        st.markdown("### 📚 Iteration History")
        
        iterations = tracker.get_all_iterations()
        
        if not iterations:
            st.info("No completed iterations yet.")
            return
        
        # Create a table of iterations
        for iteration in iterations:
            with st.expander(f"Iteration #{iteration['number']} - {'✅ Complete' if iteration['is_complete'] else '🔄 In Progress'}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Generation", f"{iteration['generation_progress']:.1f}%")
                    st.caption(f"Status: {iteration['generation_status']}")
                
                with col2:
                    st.metric("Review", f"{iteration['review_progress']:.1f}%")
                    st.caption(f"Status: {iteration['review_status']}")
                
                with col3:
                    st.metric("Duration", f"{iteration['duration']:.1f}s")
                    st.caption(f"Convergence: {iteration['convergence_score']:.2f}")
                
                # Show feedback for this iteration
                if iteration['feedback']:
                    st.markdown("**Feedback:**")
                    for feedback in iteration['feedback']:
                        st.write(f"• {feedback}")

def create_demo_loop_visualizer():
    """Create a demo of the loop visualizer."""
    st.title("🔄 Loop Visualizer Demo")
    
    # Initialize session state
    if 'demo_tracker' not in st.session_state:
        st.session_state.demo_tracker = None
        st.session_state.demo_running = False
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Demo Loop", disabled=st.session_state.demo_running):
            st.session_state.demo_tracker = LoopProgressTracker(
                convergence_threshold=0.85,
                max_iterations=3
            )
            st.session_state.demo_running = True
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Demo", disabled=not st.session_state.demo_running):
            st.session_state.demo_running = False
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset Demo"):
            st.session_state.demo_tracker = None
            st.session_state.demo_running = False
            st.rerun()
    
    # Show visualizer if we have a tracker
    if st.session_state.demo_tracker:
        visualizer = LoopVisualizer()
        
        # Run demo simulation if active
        if st.session_state.demo_running:
            _run_demo_simulation(st.session_state.demo_tracker)
        
        # Show the visualization
        visualizer.create_loop_interface(st.session_state.demo_tracker)

def _run_demo_simulation(tracker: LoopProgressTracker):
    """Run a demo simulation of the loop process."""
    
    # Start the loop if not started
    if tracker.current_state == LoopState.IDLE:
        tracker.start_loop()
    
    # Simulate progress based on current state
    if tracker.current_state == LoopState.GENERATION:
        current_progress = tracker.current_iteration.generation_progress if tracker.current_iteration else 0
        
        if current_progress < 100:
            # Simulate generation progress
            new_progress = min(current_progress + 15, 100)
            tracker.update_generation_progress(new_progress, f"Generating code... {new_progress:.0f}%")
            
            if new_progress >= 100:
                tracker.complete_generation(quality_score=0.7 + (tracker.current_iteration.iteration_number * 0.1))
        
    elif tracker.current_state == LoopState.REVIEW:
        current_progress = tracker.current_iteration.review_progress if tracker.current_iteration else 0
        
        if current_progress < 100:
            # Simulate review progress
            new_progress = min(current_progress + 20, 100)
            tracker.update_review_progress(new_progress, f"Reviewing code... {new_progress:.0f}%")
            
            # Add some demo feedback
            if new_progress == 40:
                tracker.add_feedback("Add error handling to main function")
            elif new_progress == 80:
                tracker.add_feedback("Optimize database queries for better performance")
            
            if new_progress >= 100:
                # Calculate convergence score (improves with each iteration)
                base_score = 0.6
                improvement = tracker.current_iteration.iteration_number * 0.15
                convergence_score = min(base_score + improvement, 1.0)
                tracker.complete_review(convergence_score)
    
    # Auto-refresh every 2 seconds during demo
    if tracker.current_state in [LoopState.GENERATION, LoopState.REVIEW]:
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    create_demo_loop_visualizer()
