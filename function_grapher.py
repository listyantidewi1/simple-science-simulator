import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches

# -----------------------------
# Interactive Function Grapher
# For Junior High School Math
# -----------------------------

# Function types
FUNCTION_TYPES = {
    "Linear": "y = mx + b",
    "Quadratic": "y = ax² + bx + c",
    "Exponential": "y = a·b^x + c",
    "Absolute Value": "y = a|x - h| + k",
    "Sine": "y = a·sin(bx + c) + d"
}

# Initial parameters
state = {
    "function_type": "Linear",
    "m": 1.0,      # slope (linear)
    "b": 0.0,      # y-intercept (linear)
    "a": 1.0,      # coefficient (quadratic/exponential)
    "c": 0.0,      # constant term
    "h": 0.0,      # horizontal shift
    "k": 0.0,      # vertical shift
    "b_exp": 2.0,  # base for exponential
    "freq": 1.0,   # frequency for sine
    "d": 0.0       # vertical shift for sine
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(14, 9))
plt.subplots_adjust(left=0.08, bottom=0.35, right=0.70, top=0.95)

# Main plot axes
ax = plt.subplot(1, 1, 1)
ax.set_title("Interactive Function Grapher - Junior High Math", fontsize=14, fontweight='bold')
ax.set_xlabel("x", fontsize=12)
ax.set_ylabel("y", fontsize=12)
ax.grid(True, alpha=0.3, linestyle='--')
ax.axhline(0, color='black', linewidth=0.8)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

# Function graph line
graph_line, = ax.plot([], [], 'b-', linewidth=3, label="Function", zorder=5)

# Key points markers
key_points, = ax.plot([], [], 'ro', markersize=10, label="Key Points", zorder=6)

# Equation display
equation_text = ax.text(0.02, 0.98, "", transform=ax.transAxes,
                       fontsize=12, fontweight='bold', va='top', ha='left',
                       bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.9))

# Info text panel - positioned on the right side
ax_text = plt.axes([0.70, 0.35, 0.29, 0.60])
ax_text.axis('off')
ax_text.set_xlim(0, 1)
ax_text.set_ylim(0, 1)
info_text = ax_text.text(
    0.02, 0.98, "",
    transform=ax_text.transAxes,
    va="top",
    ha="left",
    fontsize=10,
    family='monospace',
    bbox=dict(boxstyle="round,pad=0.8", facecolor="white", alpha=0.95, edgecolor="gray", linewidth=1.5)
)

ax.legend(loc="upper right", fontsize=10)

# -----------------------------
# Function definitions
# -----------------------------
def linear_func(x, m, b):
    """Linear function: y = mx + b"""
    return m * x + b

def quadratic_func(x, a, b, c):
    """Quadratic function: y = ax² + bx + c"""
    return a * x**2 + b * x + c

def exponential_func(x, a, b_base, c):
    """Exponential function: y = a·b^x + c"""
    return a * (b_base ** x) + c

def absolute_func(x, a, h, k):
    """Absolute value function: y = a|x - h| + k"""
    return a * np.abs(x - h) + k

def sine_func(x, a, freq, c, d):
    """Sine function: y = a·sin(bx + c) + d"""
    return a * np.sin(freq * x + c) + d

# -----------------------------
# Update function
# -----------------------------
def update_graph():
    """Update the graph based on current parameters."""
    x = np.linspace(-10, 10, 1000)
    
    func_type = state["function_type"]
    
    if func_type == "Linear":
        y = linear_func(x, state["m"], state["b"])
        equation = f"y = {state['m']:.2f}x + {state['b']:.2f}"
        # Key points: y-intercept and x-intercept
        key_x = [0]
        key_y = [state["b"]]
        if state["m"] != 0:
            x_int = -state["b"] / state["m"]
            if -10 <= x_int <= 10:
                key_x.append(x_int)
                key_y.append(0)
        info = (
            f"LINEAR FUNCTION\n"
            f"{'='*28}\n\n"
            f"Equation: {equation}\n\n"
            f"Parameters:\n"
            f"  m (slope) = {state['m']:.2f}\n"
            f"    • Positive = rises\n"
            f"    • Negative = falls\n"
            f"    • Steeper = larger |m|\n\n"
            f"  b (y-intercept) = {state['b']:.2f}\n"
            f"    • Where line crosses y-axis\n\n"
            f"Key Points:\n"
            f"  Y-intercept: (0, {state['b']:.2f})\n"
        )
        if state["m"] != 0:
            x_int = -state["b"] / state["m"]
            if -10 <= x_int <= 10:
                info += f"  X-intercept: ({x_int:.2f}, 0)\n"
    
    elif func_type == "Quadratic":
        y = quadratic_func(x, state["a"], state["m"], state["b"])
        equation = f"y = {state['a']:.2f}x² + {state['m']:.2f}x + {state['b']:.2f}"
        # Key points: vertex, y-intercept
        vertex_x = -state["m"] / (2 * state["a"]) if state["a"] != 0 else 0
        vertex_y = quadratic_func(vertex_x, state["a"], state["m"], state["b"])
        key_x = [0, vertex_x]
        key_y = [state["b"], vertex_y]
        info = (
            f"QUADRATIC FUNCTION\n"
            f"{'='*28}\n\n"
            f"Equation: {equation}\n\n"
            f"Parameters:\n"
            f"  a = {state['a']:.2f}\n"
            f"    • a > 0: Opens UP (U-shape)\n"
            f"    • a < 0: Opens DOWN (∩-shape)\n"
            f"    • |a| larger = narrower\n\n"
            f"  b = {state['m']:.2f}\n"
            f"    • Affects horizontal position\n\n"
            f"  c = {state['b']:.2f}\n"
            f"    • Y-intercept\n\n"
            f"Key Points:\n"
            f"  Vertex: ({vertex_x:.2f}, {vertex_y:.2f})\n"
            f"  Y-intercept: (0, {state['b']:.2f})\n"
        )
    
    elif func_type == "Exponential":
        # Limit x range to avoid overflow
        x = np.linspace(-5, 5, 1000)
        y = exponential_func(x, state["a"], state["b_exp"], state["c"])
        # Clip y values for display
        y = np.clip(y, -10, 10)
        equation = f"y = {state['a']:.2f}·{state['b_exp']:.2f}^x + {state['c']:.2f}"
        key_x = [0]
        key_y = [state["a"] + state["c"]]
        info = (
            f"EXPONENTIAL FUNCTION\n"
            f"{'='*28}\n\n"
            f"Equation: {equation}\n\n"
            f"Parameters:\n"
            f"  a = {state['a']:.2f}\n"
            f"    • Vertical stretch\n\n"
            f"  Base = {state['b_exp']:.2f}\n"
            f"    • b > 1: Grows\n"
            f"    • 0 < b < 1: Decays\n\n"
            f"  c = {state['c']:.2f}\n"
            f"    • Vertical shift\n\n"
            f"Key Points:\n"
            f"  Y-intercept: (0, {state['a'] + state['c']:.2f})\n"
        )
    
    elif func_type == "Absolute Value":
        y = absolute_func(x, state["a"], state["h"], state["k"])
        equation = f"y = {state['a']:.2f}|x - {state['h']:.2f}| + {state['k']:.2f}"
        # Key point: vertex (h, k)
        key_x = [state["h"]]
        key_y = [state["k"]]
        info = (
            f"ABSOLUTE VALUE FUNCTION\n"
            f"{'='*28}\n\n"
            f"Equation: {equation}\n\n"
            f"Parameters:\n"
            f"  a = {state['a']:.2f}\n"
            f"    • a > 0: Opens UP (V-shape)\n"
            f"    • a < 0: Opens DOWN (∧-shape)\n"
            f"    • |a| larger = steeper\n\n"
            f"  h = {state['h']:.2f}\n"
            f"    • Horizontal shift\n\n"
            f"  k = {state['k']:.2f}\n"
            f"    • Vertical shift\n\n"
            f"Key Points:\n"
            f"  Vertex: ({state['h']:.2f}, {state['k']:.2f})\n"
        )
    
    elif func_type == "Sine":
        y = sine_func(x, state["a"], state["freq"], state["c"], state["d"])
        equation = f"y = {state['a']:.2f}·sin({state['freq']:.2f}x + {state['c']:.2f}) + {state['d']:.2f}"
        # Key points: first few peaks/valleys
        key_x = [0]
        key_y = [state["d"]]
        info = (
            f"SINE FUNCTION\n"
            f"{'='*28}\n\n"
            f"Equation: {equation}\n\n"
            f"Parameters:\n"
            f"  a = {state['a']:.2f}\n"
            f"    • Amplitude (height)\n\n"
            f"  Frequency = {state['freq']:.2f}\n"
            f"    • Higher = more waves\n\n"
            f"  Phase = {state['c']:.2f}\n"
            f"    • Horizontal shift\n\n"
            f"  d = {state['d']:.2f}\n"
            f"    • Vertical shift\n\n"
            f"Key Points:\n"
            f"  Y-intercept: (0, {state['d']:.2f})\n"
        )
    
    # Update graph
    graph_line.set_data(x, y)
    
    # Update key points
    key_points.set_data(key_x, key_y)
    
    # Update equation display
    equation_text.set_text(equation)
    
    # Update info text
    info_text.set_text(info)
    
    # Auto-adjust y-axis for better view
    y_min, y_max = np.min(y), np.max(y)
    if y_max - y_min > 0.1:
        margin = (y_max - y_min) * 0.1
        ax.set_ylim(y_min - margin, y_max + margin)
    else:
        ax.set_ylim(-10, 10)
    
    fig.canvas.draw_idle()

# -----------------------------
# Controls
# -----------------------------
# Function type selector
ax_func = plt.axes([0.10, 0.25, 0.55, 0.10])
func_radio = RadioButtons(ax_func, list(FUNCTION_TYPES.keys()), active=0)

# Parameter sliders - each at unique position to avoid mouse grab conflicts
# Row 1 (y=0.20)
ax_m = plt.axes([0.10, 0.20, 0.55, 0.03])
m_slider = Slider(ax_m, "m (slope)", -5.0, 5.0, valinit=state["m"], valstep=0.1)

# Row 2 (y=0.16)
ax_b = plt.axes([0.10, 0.16, 0.55, 0.03])
b_slider = Slider(ax_b, "b (y-intercept)", -5.0, 5.0, valinit=state["b"], valstep=0.1)

# Row 3 (y=0.12)
ax_a = plt.axes([0.10, 0.12, 0.55, 0.03])
a_slider = Slider(ax_a, "a (coefficient)", -3.0, 3.0, valinit=state["a"], valstep=0.1)

# Row 4 (y=0.08)
ax_c = plt.axes([0.10, 0.08, 0.55, 0.03])
c_slider = Slider(ax_c, "c (constant)", -5.0, 5.0, valinit=state["c"], valstep=0.1)

# Row 5 (y=0.04)
ax_bexp = plt.axes([0.10, 0.04, 0.55, 0.03])
bexp_slider = Slider(ax_bexp, "Base (b)", 0.1, 5.0, valinit=state["b_exp"], valstep=0.1)

# Additional sliders at different positions to avoid overlap
# Row 1 alternate (y=0.20, right side) - for h
ax_h = plt.axes([0.68, 0.20, 0.25, 0.03])
h_slider = Slider(ax_h, "h (horizontal shift)", -5.0, 5.0, valinit=state["h"], valstep=0.1)
h_slider.ax.set_visible(False)

# Row 2 alternate (y=0.16, right side) - for k
ax_k = plt.axes([0.68, 0.16, 0.25, 0.03])
k_slider = Slider(ax_k, "k (vertical shift)", -5.0, 5.0, valinit=state["k"], valstep=0.1)
k_slider.ax.set_visible(False)

# Row 3 alternate (y=0.12, right side) - for freq
ax_freq = plt.axes([0.68, 0.12, 0.25, 0.03])
freq_slider = Slider(ax_freq, "Frequency", 0.1, 5.0, valinit=state["freq"], valstep=0.1)
freq_slider.ax.set_visible(False)

# Row 4 alternate (y=0.08, right side) - for d
ax_d = plt.axes([0.68, 0.08, 0.25, 0.03])
d_slider = Slider(ax_d, "d (vertical shift)", -5.0, 5.0, valinit=state["d"], valstep=0.1)
d_slider.ax.set_visible(False)

# Buttons
ax_reset = plt.axes([0.70, 0.25, 0.12, 0.04])
btn_reset = Button(ax_reset, "Reset")

# Sliders are already hidden above where needed

# -----------------------------
# Event handlers
# -----------------------------
def on_func_change(label):
    """Handle function type change."""
    state["function_type"] = label
    
    # Hide all sliders first (they share axes, so only one per row can be visible)
    m_slider.ax.set_visible(False)
    h_slider.ax.set_visible(False)
    b_slider.ax.set_visible(False)
    k_slider.ax.set_visible(False)
    a_slider.ax.set_visible(False)
    freq_slider.ax.set_visible(False)
    c_slider.ax.set_visible(False)
    d_slider.ax.set_visible(False)
    bexp_slider.ax.set_visible(False)
    
    # Show appropriate sliders (only one per row)
    if label == "Linear":
        m_slider.ax.set_visible(True)
        m_slider.label.set_text("m (slope)")
        b_slider.ax.set_visible(True)
        b_slider.label.set_text("b (y-intercept)")
    
    elif label == "Quadratic":
        m_slider.ax.set_visible(True)
        m_slider.label.set_text("b (coefficient of x)")
        b_slider.ax.set_visible(True)
        b_slider.label.set_text("c (constant)")
        a_slider.ax.set_visible(True)
        a_slider.label.set_text("a (coefficient)")
    
    elif label == "Exponential":
        a_slider.ax.set_visible(True)
        a_slider.label.set_text("a (coefficient)")
        c_slider.ax.set_visible(True)
        c_slider.label.set_text("c (constant)")
        bexp_slider.ax.set_visible(True)
    
    elif label == "Absolute Value":
        a_slider.ax.set_visible(True)
        a_slider.label.set_text("a (coefficient)")
        h_slider.ax.set_visible(True)
        k_slider.ax.set_visible(True)
    
    elif label == "Sine":
        a_slider.ax.set_visible(True)
        a_slider.label.set_text("a (amplitude)")
        c_slider.ax.set_visible(True)
        c_slider.label.set_text("Phase shift")
        freq_slider.ax.set_visible(True)
        d_slider.ax.set_visible(True)
    
    update_graph()
    fig.canvas.draw_idle()

def on_slider_change(val):
    """Handle slider changes."""
    state["m"] = float(m_slider.val)
    state["b"] = float(b_slider.val)
    state["a"] = float(a_slider.val)
    state["c"] = float(c_slider.val)
    state["h"] = float(h_slider.val)
    state["k"] = float(k_slider.val)
    state["b_exp"] = float(bexp_slider.val)
    state["freq"] = float(freq_slider.val)
    state["d"] = float(d_slider.val)
    update_graph()

def on_reset(_):
    """Reset all parameters to defaults."""
    state["m"] = 1.0
    state["b"] = 0.0
    state["a"] = 1.0
    state["c"] = 0.0
    state["h"] = 0.0
    state["k"] = 0.0
    state["b_exp"] = 2.0
    state["freq"] = 1.0
    state["d"] = 0.0
    
    m_slider.reset()
    b_slider.reset()
    a_slider.reset()
    c_slider.reset()
    h_slider.reset()
    k_slider.reset()
    bexp_slider.reset()
    freq_slider.reset()
    d_slider.reset()
    
    update_graph()

# Wire up events
func_radio.on_clicked(on_func_change)
m_slider.on_changed(on_slider_change)
b_slider.on_changed(on_slider_change)
a_slider.on_changed(on_slider_change)
c_slider.on_changed(on_slider_change)
h_slider.on_changed(on_slider_change)
k_slider.on_changed(on_slider_change)
bexp_slider.on_changed(on_slider_change)
freq_slider.on_changed(on_slider_change)
d_slider.on_changed(on_slider_change)
btn_reset.on_clicked(on_reset)

# Initial render
update_graph()
plt.show()

