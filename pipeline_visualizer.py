"""
Pipeline Visualizer - Creates visual representations of the Multi-Agent Pipeline
with emphasis on the Code Generation and Code Review looping mechanism.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_pipeline_diagram():
    """Create a detailed pipeline diagram showing the looping mechanism."""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Define colors
    colors = {
        'requirements': '#E3F2FD',
        'code_gen': '#E1F5FE', 
        'code_review': '#F3E5F5',
        'improvement': '#FFF3E0',
        'other_steps': '#E8F5E8',
        'decision': '#FFEBEE',
        'loop': '#FFF9C4'
    }
    
    # Title
    ax.text(5, 11.5, 'Multi-Agent Pipeline with Code Generation & Review Loop', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Step 1: Requirements Analysis
    req_box = FancyBboxPatch((0.5, 10), 2, 0.8, 
                            boxstyle="round,pad=0.1", 
                            facecolor=colors['requirements'],
                            edgecolor='black', linewidth=1.5)
    ax.add_patch(req_box)
    ax.text(1.5, 10.4, '1. Requirements\nAnalysis', ha='center', va='center', fontweight='bold')
    
    # Step 2: Initial Code Generation
    code_gen_box = FancyBboxPatch((0.5, 8.5), 2, 0.8,
                                 boxstyle="round,pad=0.1",
                                 facecolor=colors['code_gen'],
                                 edgecolor='black', linewidth=1.5)
    ax.add_patch(code_gen_box)
    ax.text(1.5, 8.9, '2. Code Generation\n(Initial)', ha='center', va='center', fontweight='bold')
    
    # Step 3: Code Review
    review_box = FancyBboxPatch((0.5, 7), 2, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['code_review'],
                               edgecolor='black', linewidth=1.5)
    ax.add_patch(review_box)
    ax.text(1.5, 7.4, '3. Code Review', ha='center', va='center', fontweight='bold')
    
    # Decision Diamond
    decision_diamond = patches.RegularPolygon((4, 7.4), 4, radius=0.6, 
                                            orientation=np.pi/4,
                                            facecolor=colors['decision'],
                                            edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_diamond)
    ax.text(4, 7.4, 'Issues\nFound?', ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Loop Back - Code Improvement
    improve_box = FancyBboxPatch((6, 8.5), 2.5, 0.8,
                                boxstyle="round,pad=0.1",
                                facecolor=colors['improvement'],
                                edgecolor='black', linewidth=1.5)
    ax.add_patch(improve_box)
    ax.text(7.25, 8.9, 'Code Improvement\nRequest', ha='center', va='center', fontweight='bold')
    
    # Improved Code Generation
    improved_gen_box = FancyBboxPatch((6, 7), 2.5, 0.8,
                                     boxstyle="round,pad=0.1",
                                     facecolor=colors['code_gen'],
                                     edgecolor='black', linewidth=1.5)
    ax.add_patch(improved_gen_box)
    ax.text(7.25, 7.4, 'Improved Code\nGeneration', ha='center', va='center', fontweight='bold')
    
    # Loop highlight box
    loop_highlight = FancyBboxPatch((3.2, 6.5), 5.5, 3,
                                   boxstyle="round,pad=0.2",
                                   facecolor=colors['loop'],
                                   edgecolor='orange', linewidth=2,
                                   linestyle='--', alpha=0.3)
    ax.add_patch(loop_highlight)
    ax.text(6, 9.7, 'ITERATIVE LOOP', ha='center', va='center', 
            fontweight='bold', fontsize=12, color='orange')
    
    # Remaining steps
    steps = [
        ('4. Documentation', 5.5),
        ('5. Test Generation', 4.5),
        ('6. Deployment Config', 3.5),
        ('7. UI Generation', 2.5)
    ]
    
    for step, y_pos in steps:
        step_box = FancyBboxPatch((0.5, y_pos), 2, 0.8,
                                 boxstyle="round,pad=0.1",
                                 facecolor=colors['other_steps'],
                                 edgecolor='black', linewidth=1.5)
        ax.add_patch(step_box)
        ax.text(1.5, y_pos + 0.4, step, ha='center', va='center', fontweight='bold')
    
    # Final Output
    output_box = FancyBboxPatch((0.5, 1), 2, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor='#FFD700',
                               edgecolor='black', linewidth=2)
    ax.add_patch(output_box)
    ax.text(1.5, 1.4, 'Final Output', ha='center', va='center', fontweight='bold')
    
    # Arrows - Main flow
    arrows = [
        # Main flow down
        ((1.5, 10), (1.5, 9.3)),
        ((1.5, 8.5), (1.5, 7.8)),
        ((2.5, 7.4), (3.4, 7.4)),
        ((1.5, 7), (1.5, 6.3)),
        ((1.5, 5.5), (1.5, 5.3)),
        ((1.5, 4.5), (1.5, 4.3)),
        ((1.5, 3.5), (1.5, 3.3)),
        ((1.5, 2.5), (1.5, 1.8)),
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Loop arrows
    # Issues found -> Improvement
    ax.annotate('', xy=(6, 8.9), xytext=(4.6, 7.4),
               arrowprops=dict(arrowstyle='->', lw=2, color='red',
                             connectionstyle="arc3,rad=0.3"))
    ax.text(5.2, 8.2, 'YES', ha='center', va='center', color='red', fontweight='bold')
    
    # Improvement -> Improved Generation
    ax.annotate('', xy=(7.25, 8.5), xytext=(7.25, 7.8),
               arrowprops=dict(arrowstyle='->', lw=2, color='orange'))
    
    # Back to review
    ax.annotate('', xy=(2.5, 7.4), xytext=(6, 7.4),
               arrowprops=dict(arrowstyle='->', lw=2, color='orange',
                             connectionstyle="arc3,rad=-0.5"))
    ax.text(4.25, 6.5, 'Re-review', ha='center', va='center', color='orange', fontweight='bold')
    
    # No issues -> Continue
    ax.text(2.8, 6.8, 'NO', ha='center', va='center', color='green', fontweight='bold')
    
    # Add timing information
    timing_info = [
        ('~25s', 1.5, 9.7),
        ('~45s', 1.5, 8.2),
        ('~30s/iter', 1.5, 6.7),
        ('~20s', 1.5, 5.2),
        ('~25s', 1.5, 4.2),
        ('~15s', 1.5, 3.2),
        ('~20s', 1.5, 2.2)
    ]
    
    for timing, x, y in timing_info:
        ax.text(x + 1.2, y, timing, ha='left', va='center', 
               fontsize=9, style='italic', color='blue')
    
    # Legend
    legend_elements = [
        patches.Patch(color=colors['requirements'], label='Requirements Analysis'),
        patches.Patch(color=colors['code_gen'], label='Code Generation'),
        patches.Patch(color=colors['code_review'], label='Code Review'),
        patches.Patch(color=colors['improvement'], label='Code Improvement'),
        patches.Patch(color=colors['other_steps'], label='Other Pipeline Steps'),
        patches.Patch(color=colors['decision'], label='Decision Point'),
        patches.Patch(color=colors['loop'], label='Iterative Loop', alpha=0.3)
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    plt.tight_layout()
    return fig

def create_loop_detail_diagram():
    """Create a detailed view of just the loop mechanism."""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(5, 7.5, 'Code Generation & Review Loop - Detailed View', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Loop steps
    steps = [
        ('Initial Code\nGeneration', 1.5, 6, '#E1F5FE'),
        ('Code Review\nAnalysis', 5, 6, '#F3E5F5'),
        ('Issue Detection\n& Feedback', 8.5, 6, '#FFEBEE'),
        ('Code Improvement\nGeneration', 8.5, 3, '#FFF3E0'),
        ('Quality Check\n& Validation', 5, 3, '#F3E5F5'),
        ('Final Approval\nor Re-iterate', 1.5, 3, '#E8F5E8')
    ]
    
    boxes = []
    for step, x, y, color in steps:
        box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8,
                            boxstyle="round,pad=0.1",
                            facecolor=color,
                            edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, step, ha='center', va='center', fontweight='bold', fontsize=10)
        boxes.append((x, y))
    
    # Arrows showing flow
    flow_arrows = [
        ((2.2, 6), (4.3, 6)),      # Initial -> Review
        ((5.7, 6), (7.8, 6)),      # Review -> Detection
        ((8.5, 5.6), (8.5, 3.4)),  # Detection -> Improvement
        ((7.8, 3), (5.7, 3)),      # Improvement -> Quality Check
        ((4.3, 3), (2.2, 3)),      # Quality -> Approval
        ((1.5, 3.4), (1.5, 5.6))   # Back to start (loop)
    ]
    
    for start, end in flow_arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    # Loop indicator
    ax.annotate('', xy=(1.5, 5.6), xytext=(1.5, 3.4),
               arrowprops=dict(arrowstyle='->', lw=3, color='red',
                             connectionstyle="arc3,rad=0.8"))
    ax.text(0.5, 4.5, 'LOOP\nUNTIL\nAPPROVED', ha='center', va='center', 
            color='red', fontweight='bold', fontsize=12)
    
    # Add decision criteria
    criteria_text = """
Loop Termination Criteria:
• No critical issues found
• Security vulnerabilities resolved
• Performance meets standards
• Code follows best practices
• All requirements satisfied
    """
    
    ax.text(5, 1.5, criteria_text, ha='center', va='top', 
           bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8),
           fontsize=10)
    
    plt.tight_layout()
    return fig

def save_diagrams():
    """Save both diagrams as PNG files."""
    
    # Create and save main pipeline diagram
    fig1 = create_pipeline_diagram()
    fig1.savefig('pipeline_with_loop.png', dpi=300, bbox_inches='tight')
    plt.close(fig1)
    
    # Create and save loop detail diagram
    fig2 = create_loop_detail_diagram()
    fig2.savefig('loop_detail.png', dpi=300, bbox_inches='tight')
    plt.close(fig2)
    
    print("Pipeline diagrams saved:")
    print("- pipeline_with_loop.png")
    print("- loop_detail.png")

if __name__ == "__main__":
    save_diagrams()
