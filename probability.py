import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon, Arc
import matplotlib.patches as mpatches
from collections import Counter

# -----------------------------
# Probability Simulator
# For Junior High School Math
# -----------------------------

# Experiment types
EXPERIMENTS = {
    "Coin Flip": "Flip a coin (heads/tails)",
    "Dice Roll": "Roll a die (1-6)",
    "Two Dice": "Roll two dice (sum 2-12)",
    "Spinner": "Spin a wheel (1-8 sections)"
}

# State
state = {
    "experiment_type": "Coin Flip",
    "num_trials": 100,
    "results": [],
    "running": False,
    "animation_frame": 0
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(14, 9))
plt.subplots_adjust(left=0.32, bottom=0.30, right=0.95, top=0.95)

# Main plot axes (for visualization) - positioned in center-right area
ax = plt.axes([0.32, 0.30, 0.35, 0.65])
ax.set_title("Probability Simulator - Junior High Math", fontsize=14, fontweight='bold')
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.axis('off')

# Visualization elements
coin_visual = None
coin_text = None
dice_visual = []
spinner_visual = None
spinner_labels = []
spinner_pointer = None
result_text = ax.text(0, 0.7, "", ha='center', va='center', fontsize=24, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.9))

# Info text panel (on the left side)
ax_text = plt.axes([0.02, 0.30, 0.28, 0.65])
ax_text.axis('off')
ax_text.set_xlim(0, 1)
ax_text.set_ylim(0, 1)
info_text = ax_text.text(
    0.02, 0.98, "",
    transform=ax_text.transAxes,
    va="top",
    ha="left",
    fontsize=8.5,
    family='monospace',
    bbox=dict(boxstyle="round,pad=1.2", facecolor="#ffffff", alpha=0.98, 
             edgecolor="#3498db", linewidth=2.5, linestyle='-')
)

# Statistics plot (histogram) - on the right side
ax_stats = plt.axes([0.68, 0.30, 0.29, 0.65])
ax_stats.set_facecolor('#f8f9fa')

# Histogram bars
bars = None

# -----------------------------
# Visualization functions
# -----------------------------
def clear_all_visualizations():
    """Clear all visualization elements."""
    global coin_visual, coin_text, dice_visual, spinner_visual, spinner_labels, spinner_pointer
    
    # Clear coin
    if coin_visual is not None:
        coin_visual.remove()
        coin_visual = None
    if coin_text is not None:
        if isinstance(coin_text, list):
            for item in coin_text:
                item.remove()
        else:
            coin_text.remove()
        coin_text = None
    
    # Clear dice
    for d in dice_visual:
        if d is not None:
            for patch in d:
                patch.remove()
    dice_visual = []
    
    # Clear spinner
    if spinner_visual is not None:
        for patch in spinner_visual:
            if patch is not None:
                try:
                    patch.remove()
                except (ValueError, AttributeError):
                    pass
        spinner_visual = None
    for label in spinner_labels:
        if label is not None:
            try:
                label.remove()
            except (ValueError, AttributeError):
                pass
    spinner_labels = []
    spinner_pointer = None  # Don't remove separately, it's in spinner_visual

def draw_coin(result=None):
    """Draw a coin visualization."""
    global coin_visual, coin_text
    
    clear_all_visualizations()
    
    # Coin circle (larger, more visible)
    coin = Circle((0, 0), 0.45, fill=True, facecolor='gold', edgecolor='black', lw=4, zorder=2)
    ax.add_patch(coin)
    coin_visual = coin
    
    if result is not None:
        # Show result with coin design
        if result == "Heads":
            # Draw a simple face/head design
            # Outer circle for head
            head = Circle((0, 0.1), 0.15, fill=True, facecolor='lightblue', edgecolor='black', lw=2, zorder=3)
            ax.add_patch(head)
            # Eyes
            eye1 = Circle((-0.05, 0.12), 0.02, fill=True, facecolor='black', zorder=4)
            eye2 = Circle((0.05, 0.12), 0.02, fill=True, facecolor='black', zorder=4)
            ax.add_patch(eye1)
            ax.add_patch(eye2)
            # Smile
            smile = Arc((0, 0.08), 0.1, 0.05, angle=0, theta1=0, theta2=180, 
                       color='black', lw=2, zorder=4)
            ax.add_patch(smile)
            coin_text = [head, eye1, eye2, smile]
            result_text.set_text("HEADS")
            result_text.set_color('blue')
        else:
            # Draw tails design (simple pattern)
            # Cross pattern or text
            from matplotlib.patches import FancyBboxPatch
            tail1 = Rectangle((-0.12, -0.12), 0.24, 0.05, fill=True, facecolor='black', zorder=3)
            tail2 = Rectangle((-0.05, -0.2), 0.1, 0.24, fill=True, facecolor='black', zorder=3)
            ax.add_patch(tail1)
            ax.add_patch(tail2)
            coin_text = [tail1, tail2]
            result_text.set_text("TAILS")
            result_text.set_color('red')
    else:
        result_text.set_text("?")
        result_text.set_color('black')

def draw_dice(value=None, num_dice=1):
    """Draw dice visualization."""
    global dice_visual
    
    clear_all_visualizations()
    
    if num_dice == 1:
        positions = [(0, 0)]
    else:
        positions = [(-0.3, 0), (0.3, 0)]
    
    for i, (x, y) in enumerate(positions):
        # Dice square
        dice_square = Rectangle((x - 0.25, y - 0.25), 0.5, 0.5, 
                               fill=True, facecolor='white', edgecolor='black', lw=2, zorder=2)
        ax.add_patch(dice_square)
        
        patches = [dice_square]
        
        if value is not None:
            if num_dice == 1:
                val = value
            else:
                val = value[i] if isinstance(value, (list, tuple)) else value
            
            # Draw dots
            dot_positions = {
                1: [(0, 0)],
                2: [(-0.15, -0.15), (0.15, 0.15)],
                3: [(-0.15, -0.15), (0, 0), (0.15, 0.15)],
                4: [(-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15)],
                5: [(-0.15, -0.15), (0.15, -0.15), (0, 0), (-0.15, 0.15), (0.15, 0.15)],
                6: [(-0.15, -0.2), (0.15, -0.2), (-0.15, 0), (0.15, 0), (-0.15, 0.2), (0.15, 0.2)]
            }
            
            dots_list = dot_positions.get(int(val), [])
            for dx, dy in dots_list:
                dot = Circle((x + dx, y + dy), 0.04, fill=True, facecolor='black', zorder=3)
                ax.add_patch(dot)
                patches.append(dot)
            
            # Don't set text here for two dice - will set after loop
            if num_dice == 1:
                result_text.set_text(str(val))
        else:
            result_text.set_text("?")
        
        dice_visual.append(patches)

def draw_spinner(result=None, num_sections=8):
    """Draw spinner visualization."""
    global spinner_visual, spinner_labels, spinner_pointer
    
    clear_all_visualizations()
    
    spinner_visual = []
    spinner_labels = []
    
    # Spinner circle
    center = (0, 0)
    radius = 0.5
    
    # Draw sections
    try:
        # Try new matplotlib API first
        colormap = plt.colormaps['Set3']
    except (AttributeError, KeyError):
        # Fallback to old API
        from matplotlib import cm
        colormap = cm.get_cmap('Set3')
    colors = colormap(np.linspace(0, 1, num_sections))
    
    for i in range(num_sections):
        angle1 = 2 * np.pi * i / num_sections
        angle2 = 2 * np.pi * (i + 1) / num_sections
        
        # Create wedge
        theta = np.linspace(angle1, angle2, 50)
        x = np.concatenate([[0], radius * np.cos(theta), [0]])
        y = np.concatenate([[0], radius * np.sin(theta), [0]])
        
        # Check if this is the winning section
        edge_color = 'yellow' if (result is not None and result == i + 1) else 'black'
        edge_width = 3 if (result is not None and result == i + 1) else 1.5
        
        wedge = Polygon(list(zip(x, y)), closed=True, 
                       facecolor=colors[i], edgecolor=edge_color, lw=edge_width, zorder=1)
        ax.add_patch(wedge)
        spinner_visual.append(wedge)
        
        # Label
        mid_angle = (angle1 + angle2) / 2
        label_x = 0.3 * np.cos(mid_angle)
        label_y = 0.3 * np.sin(mid_angle)
        label_text = ax.text(label_x, label_y, str(i + 1), ha='center', va='center', 
                            fontsize=12, fontweight='bold', zorder=3)
        spinner_labels.append(label_text)
    
    # Pointer (rotates to point at result)
    if result is not None:
        # Calculate angle for the result (center of that section)
        result_angle = 2 * np.pi * (result - 1) / num_sections + np.pi / num_sections
        # Pointer points to the result section
        pointer_tip_x = 0.5 * np.cos(result_angle)
        pointer_tip_y = 0.5 * np.sin(result_angle)
        # Create pointer triangle
        perp_angle = result_angle + np.pi / 2
        p1 = (0.05 * np.cos(result_angle), 0.05 * np.sin(result_angle))
        p2 = (pointer_tip_x + 0.08 * np.cos(perp_angle), pointer_tip_y + 0.08 * np.sin(perp_angle))
        p3 = (pointer_tip_x - 0.08 * np.cos(perp_angle), pointer_tip_y - 0.08 * np.sin(perp_angle))
        pointer = Polygon([p1, p2, p3], closed=True, facecolor='red', edgecolor='darkred', lw=2, zorder=4)
    else:
        # Default pointer position (pointing up)
        pointer = Polygon([(0, 0), (0.45, 0.1), (0.45, -0.1)], 
                         closed=True, facecolor='red', edgecolor='darkred', lw=2, zorder=4)
    
    ax.add_patch(pointer)
    spinner_visual.append(pointer)
    spinner_pointer = pointer
    
    if result is not None:
        result_text.set_text(str(result))
        result_text.set_color('green')
    else:
        result_text.set_text("?")
        result_text.set_color('black')

def update_histogram():
    """Update the histogram with current results."""
    global bars
    
    ax_stats.clear()
    ax_stats.set_facecolor('#f8f9fa')  # Light gray background
    ax_stats.set_title("Results Distribution", fontsize=13, fontweight='bold', 
                      pad=15, color='#2c3e50')
    ax_stats.set_xlabel("Outcome", fontsize=11, fontweight='bold', color='#34495e')
    ax_stats.set_ylabel("Frequency", fontsize=11, fontweight='bold', color='#34495e')
    ax_stats.grid(True, alpha=0.4, linestyle='--', linewidth=0.8, color='gray')
    ax_stats.spines['top'].set_visible(False)
    ax_stats.spines['right'].set_visible(False)
    ax_stats.spines['left'].set_color('#bdc3c7')
    ax_stats.spines['bottom'].set_color('#bdc3c7')
    
    if not state["results"]:
        ax_stats.text(0.5, 0.5, 'No data yet.\nRun an experiment!', 
                     ha='center', va='center', transform=ax_stats.transAxes,
                     fontsize=12, color='#95a5a6', style='italic')
        return
    
    # Count frequencies
    counts = Counter(state["results"])
    
    outcomes = sorted(counts.keys())
    frequencies = [counts[outcome] for outcome in outcomes]
    
    # Create color gradient based on frequency
    max_freq = max(frequencies) if frequencies else 1
    try:
        colormap = plt.colormaps['viridis']
    except (AttributeError, KeyError):
        colormap = plt.cm.get_cmap('viridis')
    colors = colormap([freq / max_freq for freq in frequencies])
    
    # Create histogram with better styling
    bars = ax_stats.bar(outcomes, frequencies, color=colors, alpha=0.85, 
                       edgecolor='white', linewidth=2, width=0.6)
    
    # Add value labels on bars with better formatting
    for i, bar in enumerate(bars):
        height = bar.get_height()
        # Position label above bar
        ax_stats.text(bar.get_x() + bar.get_width()/2., height + max_freq * 0.02,
                     f'{int(height)}',
                     ha='center', va='bottom', fontsize=10, fontweight='bold',
                     color='#2c3e50')
        # Add percentage label below
        total = len(state["results"])
        percentage = (height / total) * 100
        ax_stats.text(bar.get_x() + bar.get_width()/2., -max_freq * 0.05,
                     f'{percentage:.1f}%',
                     ha='center', va='top', fontsize=8, color='#7f8c8d', style='italic')
    
    ax_stats.set_xticks(outcomes)
    ax_stats.tick_params(axis='both', which='major', labelsize=10, colors='#34495e')
    ax_stats.set_ylim(-max_freq * 0.1, max(frequencies) * 1.15 if frequencies else 1)

def update_info():
    """Update information panel."""
    exp_type = state["experiment_type"]
    num_trials = state["num_trials"]
    results = state["results"]
    
    if not results:
        info = (
            f"╔═══════════════════════════╗\n"
            f"║ PROBABILITY SIMULATOR     ║\n"
            f"╚═══════════════════════════╝\n\n"
            f"[*] Experiment: {exp_type}\n"
            f"[#] Trials: {num_trials}\n\n"
            f"[>] Click 'Run' to start!\n\n"
            f"[i] Learn about:\n"
            f"  • Probability\n"
            f"  • Frequency\n"
            f"  • Statistics"
        )
    else:
        counts = Counter(results)
        total = len(results)
        
        # Calculate probabilities
        prob_info = ""
        for outcome in sorted(counts.keys()):
            count = counts[outcome]
            prob = count / total
            # Wrap long lines
            outcome_str = str(outcome)
            if len(outcome_str) > 12:
                outcome_str = outcome_str[:10] + "..."
            prob_info += f"  {outcome_str:15s} {count:4d}/{total}\n"
            prob_info += f"  {'':15s} {prob:6.1%}\n"
        
        info = (
            f"╔═══════════════════════════╗\n"
            f"║ PROBABILITY SIMULATOR     ║\n"
            f"╚═══════════════════════════╝\n\n"
            f"[*] Experiment: {exp_type}\n"
            f"[#] Trials: {total}\n\n"
            f"[+] Results:\n{prob_info}"
        )
        
        # Add expected probabilities
        info += f"\n[!] Expected:\n"
        if exp_type == "Coin Flip":
            info += f"  50.0% each\n"
        elif exp_type == "Dice Roll":
            info += f"  16.7% each\n"
        elif exp_type == "Two Dice":
            info += f"  Most likely: 7\n"
            info += f"  (16.7%)\n"
        elif exp_type == "Spinner":
            info += f"  12.5% each\n"
    
    info_text.set_text(info)

# -----------------------------
# Experiment functions
# -----------------------------
def run_coin_flip():
    """Run coin flip experiment."""
    result = np.random.choice(["Heads", "Tails"])
    state["results"].append(result)
    draw_coin(result)
    return result

def run_dice_roll():
    """Run single dice roll."""
    result = np.random.randint(1, 7)
    state["results"].append(result)
    draw_dice(result, num_dice=1)
    return result

def run_two_dice():
    """Run two dice experiment."""
    die1 = np.random.randint(1, 7)
    die2 = np.random.randint(1, 7)
    total = die1 + die2
    state["results"].append(total)
    draw_dice((die1, die2), num_dice=2)
    return total

def run_spinner():
    """Run spinner experiment."""
    result = np.random.randint(1, 9)
    state["results"].append(result)
    draw_spinner(result, num_sections=8)
    return result

# -----------------------------
# Controls
# -----------------------------
# Experiment type selector
ax_exp = plt.axes([0.10, 0.25, 0.55, 0.10])
exp_radio = RadioButtons(ax_exp, list(EXPERIMENTS.keys()), active=0)

# Number of trials slider
ax_trials = plt.axes([0.10, 0.20, 0.55, 0.03])
trials_slider = Slider(ax_trials, "Number of trials", 10, 1000, valinit=100, valstep=10)

# Buttons
ax_run = plt.axes([0.10, 0.12, 0.12, 0.04])
btn_run = Button(ax_run, "Run")

ax_step = plt.axes([0.24, 0.12, 0.12, 0.04])
btn_step = Button(ax_step, "Step (1)")

ax_clear = plt.axes([0.38, 0.12, 0.12, 0.04])
btn_clear = Button(ax_clear, "Clear")

ax_reset = plt.axes([0.52, 0.12, 0.12, 0.04])
btn_reset = Button(ax_reset, "Reset")

# Animation control
ax_anim = plt.axes([0.10, 0.06, 0.55, 0.03])
anim_slider = Slider(ax_anim, "Animation speed", 1, 10, valinit=5, valstep=1)

# -----------------------------
# Event handlers
# -----------------------------
def on_exp_change(label):
    """Handle experiment type change."""
    state["experiment_type"] = label
    state["results"] = []
    
    # Clear everything first
    clear_all_visualizations()
    ax.clear()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis('off')
    ax.set_title("Probability Simulator - Junior High Math", fontsize=14, fontweight='bold')
    
    # Recreate result text
    global result_text
    result_text = ax.text(0, 0.7, "", ha='center', va='center', fontsize=24, fontweight='bold',
                         bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.9))
    
    # Draw initial visualization
    if label == "Coin Flip":
        draw_coin()
    elif label == "Dice Roll":
        draw_dice()
    elif label == "Two Dice":
        draw_dice(num_dice=2)
    elif label == "Spinner":
        draw_spinner(num_sections=8)
    
    update_histogram()
    update_info()
    fig.canvas.draw_idle()

def on_trials_change(val):
    """Handle trials slider change."""
    state["num_trials"] = int(val)

def run_experiment():
    """Run the full experiment."""
    state["results"] = []
    exp_type = state["experiment_type"]
    num_trials = state["num_trials"]
    
    for i in range(num_trials):
        if exp_type == "Coin Flip":
            run_coin_flip()
        elif exp_type == "Dice Roll":
            run_dice_roll()
        elif exp_type == "Two Dice":
            run_two_dice()
        elif exp_type == "Spinner":
            run_spinner()
        
        # Update every 10 trials for performance
        if (i + 1) % 10 == 0 or i == num_trials - 1:
            update_histogram()
            update_info()
            fig.canvas.draw_idle()
            fig.canvas.flush_events()
    
    # Final visualization
    if exp_type == "Coin Flip":
        draw_coin(state["results"][-1] if state["results"] else None)
    elif exp_type == "Dice Roll":
        draw_dice(state["results"][-1] if state["results"] else None)
    elif exp_type == "Two Dice":
        if state["results"]:
            last_sum = state["results"][-1]
            # Reconstruct dice values (approximate)
            die1 = min(6, max(1, last_sum // 2))
            die2 = last_sum - die1
            draw_dice((die1, die2), num_dice=2)
    elif exp_type == "Spinner":
        draw_spinner(state["results"][-1] if state["results"] else None)
    
    update_histogram()
    update_info()
    fig.canvas.draw_idle()

def on_run(_):
    """Handle run button."""
    run_experiment()

def on_step(_):
    """Handle step button (single trial)."""
    exp_type = state["experiment_type"]
    
    if exp_type == "Coin Flip":
        run_coin_flip()
    elif exp_type == "Dice Roll":
        run_dice_roll()
    elif exp_type == "Two Dice":
        run_two_dice()
    elif exp_type == "Spinner":
        run_spinner()
    
    update_histogram()
    update_info()
    fig.canvas.draw_idle()

def on_clear(_):
    """Clear results but keep experiment."""
    state["results"] = []
    
    # Reset visualization
    exp_type = state["experiment_type"]
    if exp_type == "Coin Flip":
        draw_coin()
    elif exp_type == "Dice Roll":
        draw_dice()
    elif exp_type == "Two Dice":
        draw_dice(num_dice=2)
    elif exp_type == "Spinner":
        draw_spinner(num_sections=8)
    
    update_histogram()
    update_info()
    fig.canvas.draw_idle()

def on_reset(_):
    """Reset everything."""
    state["results"] = []
    state["num_trials"] = 100
    trials_slider.reset()
    
    # Reset visualization
    exp_type = state["experiment_type"]
    if exp_type == "Coin Flip":
        draw_coin()
    elif exp_type == "Dice Roll":
        draw_dice()
    elif exp_type == "Two Dice":
        draw_dice(num_dice=2)
    elif exp_type == "Spinner":
        draw_spinner(num_sections=8)
    
    update_histogram()
    update_info()
    fig.canvas.draw_idle()

# Wire up events
exp_radio.on_clicked(on_exp_change)
trials_slider.on_changed(on_trials_change)
btn_run.on_clicked(on_run)
btn_step.on_clicked(on_step)
btn_clear.on_clicked(on_clear)
btn_reset.on_clicked(on_reset)

# Initial visualization
draw_coin()
update_info()
plt.show()

