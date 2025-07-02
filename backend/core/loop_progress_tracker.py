"""
Enhanced Loop Progress Tracker for visualizing iterative processes
like code generation and review loops.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class LoopState(Enum):
    """States for the loop process."""
    IDLE = "idle"
    GENERATION = "generation"
    REVIEW = "review"
    CONVERGING = "converging"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class LoopIteration:
    """Represents a single iteration of the generation-review loop."""
    iteration_number: int
    start_time: float
    end_time: Optional[float] = None
    generation_progress: float = 0.0
    review_progress: float = 0.0
    generation_status: str = "pending"
    review_status: str = "pending"
    feedback: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    convergence_score: float = 0.0
    
    @property
    def duration(self) -> float:
        """Get iteration duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def is_complete(self) -> bool:
        """Check if iteration is complete."""
        return self.generation_status == "completed" and self.review_status == "completed"

class LoopProgressTracker:
    """Enhanced progress tracker for generation-review loops."""
    
    def __init__(self, convergence_threshold: float = 0.9, max_iterations: int = 5):
        self.convergence_threshold = convergence_threshold
        self.max_iterations = max_iterations
        self.current_state = LoopState.IDLE
        self.iterations: List[LoopIteration] = []
        self.current_iteration: Optional[LoopIteration] = None
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.logs: List[Dict[str, Any]] = []
        self.active_process = None  # "generation" or "review"
        
    def start_loop(self) -> None:
        """Start the generation-review loop."""
        self.current_state = LoopState.GENERATION
        self.start_time = time.time()
        self.add_log("Starting generation-review loop", "info")
        self._start_new_iteration()
    
    def _start_new_iteration(self) -> None:
        """Start a new loop iteration."""
        iteration_number = len(self.iterations) + 1
        self.current_iteration = LoopIteration(
            iteration_number=iteration_number,
            start_time=time.time()
        )
        self.iterations.append(self.current_iteration)
        self.add_log(f"Starting iteration #{iteration_number}", "info")
    
    def start_generation(self) -> None:
        """Start the code generation phase."""
        if not self.current_iteration:
            self._start_new_iteration()
        
        self.current_state = LoopState.GENERATION
        self.active_process = "generation"
        self.current_iteration.generation_status = "running"
        self.add_log("Starting code generation", "info", "generation")
    
    def update_generation_progress(self, progress: float, status: str = "") -> None:
        """Update generation progress."""
        if self.current_iteration:
            self.current_iteration.generation_progress = min(progress, 100.0)
            if status:
                self.add_log(f"Generation: {status}", "info", "generation")
    
    def complete_generation(self, quality_score: float = 0.0) -> None:
        """Complete the generation phase."""
        if self.current_iteration:
            self.current_iteration.generation_status = "completed"
            self.current_iteration.generation_progress = 100.0
            self.current_iteration.quality_score = quality_score
            self.add_log("Code generation completed", "success", "generation")
            
            # Automatically start review phase
            self.start_review()
    
    def start_review(self) -> None:
        """Start the code review phase."""
        self.current_state = LoopState.REVIEW
        self.active_process = "review"
        if self.current_iteration:
            self.current_iteration.review_status = "running"
        self.add_log("Starting code review", "info", "review")
    
    def update_review_progress(self, progress: float, status: str = "") -> None:
        """Update review progress."""
        if self.current_iteration:
            self.current_iteration.review_progress = min(progress, 100.0)
            if status:
                self.add_log(f"Review: {status}", "info", "review")
    
    def add_feedback(self, feedback: str) -> None:
        """Add feedback from the review process."""
        if self.current_iteration:
            self.current_iteration.feedback.append(feedback)
            self.add_log(f"Feedback: {feedback}", "info", "review")
    
    def complete_review(self, convergence_score: float) -> None:
        """Complete the review phase and determine next action."""
        if not self.current_iteration:
            return
            
        self.current_iteration.review_status = "completed"
        self.current_iteration.review_progress = 100.0
        self.current_iteration.convergence_score = convergence_score
        self.current_iteration.end_time = time.time()
        
        self.add_log(f"Review completed. Convergence score: {convergence_score:.2f}", "success", "review")
        
        # Check if we should continue or finish
        if convergence_score >= self.convergence_threshold:
            self._complete_loop()
        elif len(self.iterations) >= self.max_iterations:
            self.add_log("Maximum iterations reached", "warning")
            self._complete_loop()
        else:
            # Start next iteration
            self.add_log("Starting next iteration based on feedback", "info")
            self._start_new_iteration()
            self.start_generation()
    
    def _complete_loop(self) -> None:
        """Complete the entire loop process."""
        self.current_state = LoopState.COMPLETED
        self.active_process = None
        self.end_time = time.time()
        self.add_log("Generation-review loop completed successfully", "success")
    
    def fail_loop(self, error: str) -> None:
        """Mark the loop as failed."""
        self.current_state = LoopState.FAILED
        self.active_process = None
        self.end_time = time.time()
        self.add_log(f"Loop failed: {error}", "error")
    
    def add_log(self, message: str, level: str = "info", source: str = "system") -> None:
        """Add a log entry."""
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'level': level,
            'source': source
        })
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current loop status."""
        current_iteration = self.current_iteration
        
        status = {
            'state': self.current_state.value,
            'active_process': self.active_process,
            'total_iterations': len(self.iterations),
            'max_iterations': self.max_iterations,
            'convergence_threshold': self.convergence_threshold,
            'is_running': self.current_state in [LoopState.GENERATION, LoopState.REVIEW],
            'is_completed': self.current_state == LoopState.COMPLETED,
            'has_failed': self.current_state == LoopState.FAILED,
            'total_duration': self.get_total_duration(),
            'current_iteration': None
        }
        
        if current_iteration:
            status['current_iteration'] = {
                'number': current_iteration.iteration_number,
                'generation_progress': current_iteration.generation_progress,
                'review_progress': current_iteration.review_progress,
                'generation_status': current_iteration.generation_status,
                'review_status': current_iteration.review_status,
                'quality_score': current_iteration.quality_score,
                'convergence_score': current_iteration.convergence_score,
                'feedback_count': len(current_iteration.feedback),
                'latest_feedback': current_iteration.feedback[-3:] if current_iteration.feedback else [],
                'duration': current_iteration.duration
            }
        
        return status
    
    def get_all_iterations(self) -> List[Dict[str, Any]]:
        """Get data for all iterations."""
        return [
            {
                'number': iteration.iteration_number,
                'generation_progress': iteration.generation_progress,
                'review_progress': iteration.review_progress,
                'generation_status': iteration.generation_status,
                'review_status': iteration.review_status,
                'quality_score': iteration.quality_score,
                'convergence_score': iteration.convergence_score,
                'feedback': iteration.feedback,
                'duration': iteration.duration,
                'is_complete': iteration.is_complete
            }
            for iteration in self.iterations
        ]
    
    def get_convergence_progress(self) -> float:
        """Get overall convergence progress as percentage."""
        if not self.iterations:
            return 0.0
        
        latest_iteration = self.iterations[-1]
        return min(latest_iteration.convergence_score / self.convergence_threshold * 100, 100.0)
    
    def get_total_duration(self) -> float:
        """Get total loop duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def get_recent_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent log entries."""
        return self.logs[-count:] if self.logs else []
    
    def should_continue_loop(self) -> bool:
        """Check if the loop should continue."""
        if not self.current_iteration:
            return True
        
        return (
            self.current_iteration.convergence_score < self.convergence_threshold and
            len(self.iterations) < self.max_iterations and
            self.current_state not in [LoopState.COMPLETED, LoopState.FAILED]
        )
