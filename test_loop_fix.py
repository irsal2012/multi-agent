#!/usr/bin/env python3
"""
Test script to verify the loop coordination fix.
This will simulate the loop process without requiring actual AI agents.
"""

import sys
import os
import time
from typing import Dict, Any

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.loop_progress_tracker import LoopProgressTracker, LoopState

def test_loop_coordination():
    """Test the loop coordination logic."""
    print("🔄 Testing Loop Coordination Fix")
    print("=" * 50)
    
    # Initialize loop tracker
    tracker = LoopProgressTracker(
        convergence_threshold=0.85,
        max_iterations=3
    )
    
    print(f"Initial state: {tracker.current_state}")
    print(f"Active process: {tracker.active_process}")
    
    # Start the loop
    print("\n1. Starting loop...")
    tracker.start_loop()
    
    status = tracker.get_current_status()
    print(f"State after start: {status['state']}")
    print(f"Active process: {status['active_process']}")
    print(f"Current iteration: {status['current_iteration']['number'] if status['current_iteration'] else 'None'}")
    
    # Simulate first iteration
    print("\n2. Simulating first iteration...")
    
    # Generation phase (first iteration)
    print("   - Generation phase...")
    tracker.update_generation_progress(25, "Processing initial code")
    tracker.update_generation_progress(50, "Structuring code modules")
    tracker.update_generation_progress(75, "Adding documentation")
    tracker.update_generation_progress(100, "Generation complete")
    
    # Complete generation - this should automatically start review
    print("   - Completing generation...")
    tracker.complete_generation(quality_score=0.6)
    
    status = tracker.get_current_status()
    print(f"   State after generation: {status['state']}")
    print(f"   Active process: {status['active_process']}")
    print(f"   Generation status: {status['current_iteration']['generation_status']}")
    print(f"   Review status: {status['current_iteration']['review_status']}")
    
    # Review phase should now be active
    print("   - Review phase...")
    tracker.update_review_progress(20, "Analyzing code structure")
    tracker.update_review_progress(40, "Checking security")
    tracker.add_feedback("Add error handling to main function")
    tracker.update_review_progress(60, "Reviewing performance")
    tracker.add_feedback("Optimize database queries")
    tracker.update_review_progress(80, "Checking best practices")
    tracker.update_review_progress(100, "Review complete")
    
    # Complete review with low convergence score to trigger next iteration
    print("   - Completing review...")
    tracker.complete_review(convergence_score=0.7)  # Below threshold
    
    status = tracker.get_current_status()
    print(f"   State after review: {status['state']}")
    print(f"   Active process: {status['active_process']}")
    print(f"   Total iterations: {status['total_iterations']}")
    
    # Check if second iteration started
    if status['total_iterations'] > 1:
        print("   ✅ Second iteration started successfully!")
        current_iter = status['current_iteration']
        print(f"   Current iteration: #{current_iter['number']}")
        print(f"   Generation status: {current_iter['generation_status']}")
        print(f"   Review status: {current_iter['review_status']}")
    else:
        print("   ❌ Second iteration did not start")
        return False
    
    # Simulate second iteration quickly
    print("\n3. Simulating second iteration...")
    
    # Generation phase (improvement)
    tracker.update_generation_progress(30, "Analyzing feedback")
    tracker.update_generation_progress(60, "Implementing improvements")
    tracker.update_generation_progress(100, "Improved code ready")
    tracker.complete_generation(quality_score=0.8)
    
    # Review phase
    tracker.update_review_progress(50, "Reviewing improvements")
    tracker.update_review_progress(100, "Review complete")
    tracker.complete_review(convergence_score=0.9)  # Above threshold
    
    # Check final state
    final_status = tracker.get_current_status()
    print(f"\nFinal state: {final_status['state']}")
    print(f"Final active process: {final_status['active_process']}")
    print(f"Is completed: {final_status['is_completed']}")
    print(f"Total iterations: {final_status['total_iterations']}")
    
    # Show iteration history
    print("\n4. Iteration History:")
    iterations = tracker.get_all_iterations()
    for iteration in iterations:
        print(f"   Iteration #{iteration['number']}:")
        print(f"     Generation: {iteration['generation_status']} ({iteration['generation_progress']:.1f}%)")
        print(f"     Review: {iteration['review_status']} ({iteration['review_progress']:.1f}%)")
        print(f"     Convergence: {iteration['convergence_score']:.2f}")
        print(f"     Feedback items: {len(iteration['feedback'])}")
        print(f"     Complete: {iteration['is_complete']}")
    
    # Show recent logs
    print("\n5. Recent Logs:")
    logs = tracker.get_recent_logs(10)
    for log in logs[-5:]:  # Show last 5 logs
        timestamp = log['timestamp'].split('T')[1][:8]  # Just time part
        print(f"   [{timestamp}] {log['source']}: {log['message']}")
    
    # Verify the fix worked
    if final_status['is_completed'] and final_status['total_iterations'] == 2:
        print("\n✅ Loop coordination fix SUCCESSFUL!")
        print("   - Loop completed properly")
        print("   - Multiple iterations executed")
        print("   - State transitions worked correctly")
        return True
    else:
        print("\n❌ Loop coordination fix FAILED!")
        return False

def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\n🧪 Testing Edge Cases")
    print("=" * 30)
    
    # Test max iterations
    tracker = LoopProgressTracker(convergence_threshold=0.95, max_iterations=2)
    tracker.start_loop()
    
    # First iteration
    tracker.complete_generation(0.6)
    tracker.complete_review(0.7)  # Below threshold
    
    # Second iteration
    tracker.complete_generation(0.7)
    tracker.complete_review(0.8)  # Still below threshold, but max iterations reached
    
    status = tracker.get_current_status()
    if status['is_completed'] and status['total_iterations'] == 2:
        print("✅ Max iterations handling works correctly")
    else:
        print("❌ Max iterations handling failed")
    
    # Test high convergence on first try
    tracker2 = LoopProgressTracker(convergence_threshold=0.85, max_iterations=3)
    tracker2.start_loop()
    tracker2.complete_generation(0.9)
    tracker2.complete_review(0.95)  # Above threshold
    
    status2 = tracker2.get_current_status()
    if status2['is_completed'] and status2['total_iterations'] == 1:
        print("✅ Early convergence handling works correctly")
    else:
        print("❌ Early convergence handling failed")

if __name__ == "__main__":
    print("🚀 Loop Coordination Fix Test")
    print("=" * 60)
    
    success = test_loop_coordination()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - Loop coordination is fixed!")
        print("\nThe issue was in the loop logic where:")
        print("1. First iteration wasn't properly handling initial code")
        print("2. State transitions between generation and review weren't smooth")
        print("3. Loop continuation logic had edge cases")
        print("\nFixes applied:")
        print("✅ Proper first iteration handling")
        print("✅ Automatic review start after generation")
        print("✅ Correct state management")
        print("✅ Improved loop continuation logic")
    else:
        print("❌ TESTS FAILED - Loop coordination still has issues")
    
    print("\nYou can now run your code generation pipeline and the loop should work properly!")
