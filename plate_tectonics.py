import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches

# -----------------------------
# Plate Tectonics Simulator
# For Junior High School Geography
# -----------------------------

# Boundary types
BOUNDARY_TYPES = {
    "Convergent": "Plates move together",
    "Divergent": "Plates move apart",
    "Transform": "Plates slide past"
}

# State
state = {
    "boundary_type": "Convergent",
    "movement_speed": 50,  # 0-100
    "animate": False,
    "time": 0.0
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(14, 9))
plt.subplots_adjust(left=0.08, bottom=0.25, right=0.68, top=0.95)

# Main visualization axes
ax = plt.axes([0.08, 0.30, 0.58, 0.65])
ax.set_title("Plate Tectonics Simulator - Junior High Geography", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.axis('off')
ax.set_facecolor('#e3f2fd')  # Light blue background

# Visual elements
plate_left = None
plate_right = None
mountains = []
volcanoes = []
earthquakes = []
rift_valley = None
fault_line = None
arrows = []
boundary_marker = None

# Info panel
ax_info = plt.axes([0.68, 0.30, 0.30, 0.65])
ax_info.axis('off')
ax_info.set_xlim(0, 1)
ax_info.set_ylim(0, 1)
info_text = ax_info.text(
    0.05, 0.98, "",
    transform=ax_info.transAxes,
    va="top",
    ha="left",
    fontsize=9,
    family='monospace',
    bbox=dict(boxstyle="round,pad=1.0", facecolor="#ffffff", alpha=0.95, 
             edgecolor="#1976d2", linewidth=2)
)

# -----------------------------
# Visualization Functions
# -----------------------------
def clear_visualization():
    """Clear all visual elements."""
    global plate_left, plate_right, mountains, volcanoes, earthquakes
    global rift_valley, fault_line, arrows, boundary_marker
    
    # Clear boundary_marker first (before checking)
    if boundary_marker is not None:
        try:
            boundary_marker.remove()
        except (ValueError, AttributeError):
            pass
        boundary_marker = None
    
    if plate_left is not None:
        try:
            if isinstance(plate_left, list):
                for patch in plate_left:
                    patch.remove()
            else:
                plate_left.remove()
        except (ValueError, AttributeError):
            pass
        plate_left = None
    
    if plate_right is not None:
        try:
            if isinstance(plate_right, list):
                for patch in plate_right:
                    patch.remove()
            else:
                plate_right.remove()
        except (ValueError, AttributeError):
            pass
        plate_right = None
    
    for mtn in mountains:
        try:
            mtn.remove()
        except (ValueError, AttributeError):
            pass
    mountains = []
    
    for volc in volcanoes:
        try:
            volc.remove()
        except (ValueError, AttributeError):
            pass
    volcanoes = []
    
    for eq in earthquakes:
        try:
            eq.remove()
        except (ValueError, AttributeError):
            pass
    earthquakes = []
    
    if rift_valley is not None:
        try:
            rift_valley.remove()
        except (ValueError, AttributeError):
            pass
        rift_valley = None
    
    if fault_line is not None:
        try:
            fault_line.remove()
        except (ValueError, AttributeError):
            pass
        fault_line = None
    
    for arrow in arrows:
        try:
            arrow.remove()
        except (ValueError, AttributeError):
            pass
    arrows = []

def clear_text_elements():
    """Clear all text elements from axes."""
    texts_to_remove = []
    for text in ax.texts:
        texts_to_remove.append(text)
    for text in texts_to_remove:
        try:
            text.remove()
        except (ValueError, AttributeError):
            pass

def draw_plates():
    """Draw the tectonic plates visualization."""
    global plate_left, plate_right, boundary_marker, rift_valley, fault_line
    
    clear_visualization()
    clear_text_elements()  # Clear text labels
    
    boundary = state["boundary_type"]
    speed = state["movement_speed"]
    time = state["time"]
    
    # Calculate plate positions based on boundary type and time
    if boundary == "Convergent":
        # Plates moving together
        offset = -0.3 + (speed / 100) * time * 0.1
        offset = max(-0.4, min(0.0, offset))
        
        # Left plate (with label)
        global plate_left
        plate_left = Rectangle((-1, -0.8), 1 + offset, 1.6,
                              facecolor='#8d6e63', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_left)
        ax.text(-0.5, 0, "PLATE A", ha='center', va='center', 
               fontsize=14, fontweight='bold', color='white', zorder=3)
        
        # Right plate (with label)
        global plate_right
        plate_right = Rectangle((offset, -0.8), 1 - offset, 1.6,
                               facecolor='#6d4c41', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_right)
        ax.text(0.5, 0, "PLATE B", ha='center', va='center', 
               fontsize=14, fontweight='bold', color='white', zorder=3)
        
        # Draw mountains at boundary (collision zone)
        if offset < -0.1:
            num_mountains = int(abs(offset) * 10) + 2
            for i in range(min(num_mountains, 5)):
                x = offset + (i - 2) * 0.15
                height = 0.2 + abs(offset) * 0.3
                # Mountain triangle
                mtn_points = [
                    (x, -0.8),
                    (x - 0.12, -0.8 + height),
                    (x + 0.12, -0.8 + height)
                ]
                mtn = Polygon(mtn_points, closed=True, facecolor='#757575', 
                             edgecolor='#424242', lw=2, zorder=3)
                ax.add_patch(mtn)
                mountains.append(mtn)
            
            # Label mountains
            if mountains:
                ax.text(offset, -0.5, "MOUNTAINS\nFORMING!", ha='center', va='center',
                       fontsize=12, fontweight='bold', color='darkred',
                       bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.9),
                       zorder=6)
        
        # Draw volcano
        if offset < -0.15:
            volc_x = offset + 0.3
            # Volcano base
            volc_base = Circle((volc_x, -0.6), 0.08, facecolor='#424242', zorder=3)
            ax.add_patch(volc_base)
            # Volcano cone
            volc_points = [
                (volc_x - 0.08, -0.6),
                (volc_x, -0.4),
                (volc_x + 0.08, -0.6)
            ]
            volc = Polygon(volc_points, closed=True, facecolor='#616161', 
                           edgecolor='#424242', lw=2, zorder=3)
            ax.add_patch(volc)
            volcanoes.append(volc_base)
            volcanoes.append(volc)
        
        # Movement arrows (pointing toward boundary) - larger and clearer
        arrow1 = FancyArrowPatch((-0.8, 0.5), (offset + 0.2, 0.5),
                                arrowstyle='->', mutation_scale=25, 
                                color='blue', linewidth=3, zorder=4)
        ax.add_patch(arrow1)
        arrows.append(arrow1)
        ax.text(-0.3, 0.6, "MOVING", ha='center', fontsize=10, 
               fontweight='bold', color='blue', zorder=5)
        
        arrow2 = FancyArrowPatch((0.8, -0.5), (offset - 0.2, -0.5),
                                arrowstyle='->', mutation_scale=25, 
                                color='blue', linewidth=3, zorder=4)
        ax.add_patch(arrow2)
        arrows.append(arrow2)
        ax.text(0.3, -0.6, "MOVING", ha='center', fontsize=10, 
               fontweight='bold', color='blue', zorder=5)
        
        # Boundary marker - thicker and more visible
        boundary_marker = Line2D([offset, offset], [-0.8, 0.8], 
                                color='red', linewidth=5, linestyle='--', 
                                alpha=0.8, zorder=5)
        ax.add_line(boundary_marker)
        
        # Boundary label
        ax.text(offset, 0.9, "COLLISION ZONE", ha='center', fontsize=11,
               fontweight='bold', color='red',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
               zorder=6)
        
    elif boundary == "Divergent":
        # Plates moving apart
        offset = 0.0 + (speed / 100) * time * 0.1
        offset = min(0.3, offset)
        
        # Left plate (with label)
        plate_left = Rectangle((-1, -0.8), 0.5 + offset, 1.6,
                              facecolor='#8d6e63', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_left)
        ax.text(-0.5, 0, "PLATE A", ha='center', va='center', 
               fontsize=14, fontweight='bold', color='white', zorder=3)
        
        # Right plate (with label)
        plate_right = Rectangle((0.5 - offset, -0.8), 0.5 + offset, 1.6,
                               facecolor='#6d4c41', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_right)
        ax.text(0.5, 0, "PLATE B", ha='center', va='center', 
               fontsize=14, fontweight='bold', color='white', zorder=3)
        
        # Rift valley (gap between plates) - more visible
        if offset > 0.05:
            global rift_valley
            rift_valley = Rectangle((0.5 - offset, -0.8), offset * 2, 1.6,
                                   facecolor='#ff6f00', edgecolor='#e65100', 
                                   lw=3, alpha=0.8, zorder=1)
            ax.add_patch(rift_valley)
            # Label the rift
            ax.text(0, 0, "RIFT\nVALLEY", ha='center', va='center',
                   fontsize=12, fontweight='bold', color='darkorange',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.9),
                   zorder=6)
        
        # Movement arrows (pointing away from boundary) - larger
        arrow1 = FancyArrowPatch((-0.2, 0.5), (-0.7, 0.5),
                                arrowstyle='->', mutation_scale=25, 
                                color='blue', linewidth=3, zorder=4)
        ax.add_patch(arrow1)
        arrows.append(arrow1)
        ax.text(-0.45, 0.6, "MOVING\nAPART", ha='center', fontsize=10, 
               fontweight='bold', color='blue', zorder=5)
        
        arrow2 = FancyArrowPatch((0.2, -0.5), (0.7, -0.5),
                                arrowstyle='->', mutation_scale=25, 
                                color='blue', linewidth=3, zorder=4)
        ax.add_patch(arrow2)
        arrows.append(arrow2)
        ax.text(0.45, -0.6, "MOVING\nAPART", ha='center', fontsize=10, 
               fontweight='bold', color='blue', zorder=5)
        
        # Boundary marker - thicker
        boundary_marker = Line2D([0, 0], [-0.8, 0.8], 
                                color='red', linewidth=5, linestyle='--', 
                                alpha=0.8, zorder=5)
        ax.add_line(boundary_marker)
        
        # Boundary label
        ax.text(0, 0.9, "DIVERGENT BOUNDARY", ha='center', fontsize=11,
               fontweight='bold', color='red',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
               zorder=6)
        
    elif boundary == "Transform":
        # Plates sliding past each other
        offset = (speed / 100) * time * 0.2
        offset = offset % 0.6 - 0.3  # Oscillating movement
        
        # Left plate (top and bottom pieces with labels)
        plate_left_top = Rectangle((-1, -0.8 + 0.8 + offset), 1, 0.8 - offset,
                              facecolor='#8d6e63', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_left_top)
        ax.text(-0.5, 0.3, "PLATE A", ha='center', va='center', 
               fontsize=12, fontweight='bold', color='white', zorder=3)
        
        plate_left_bottom = Rectangle((-1, -0.8), 1, 0.8 + offset,
                                      facecolor='#8d6e63', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_left_bottom)
        
        # Right plate (top and bottom pieces with labels)
        plate_right_bottom = Rectangle((0, -0.8), 1, 0.8 - offset,
                               facecolor='#6d4c41', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_right_bottom)
        ax.text(0.5, -0.3, "PLATE B", ha='center', va='center', 
               fontsize=12, fontweight='bold', color='white', zorder=3)
        
        plate_right_top = Rectangle((0, -0.8 + 0.8 - offset), 1, 0.8 + offset,
                                   facecolor='#6d4c41', edgecolor='#5d4037', lw=4, zorder=2)
        ax.add_patch(plate_right_top)
        
        # Fault line - thicker and more visible
        fault_y = -0.8 + 0.8 + offset
        fault_line = Line2D([-1, 1], [fault_y, fault_y], 
                           color='red', linewidth=5, linestyle='--', 
                           alpha=0.8, zorder=5)
        ax.add_line(fault_line)
        
        # Movement arrows (horizontal, opposite directions) - larger
        arrow1 = FancyArrowPatch((-0.5, -0.4), (-0.8, -0.4),
                                arrowstyle='->', mutation_scale=25, 
                                color='blue', linewidth=3, zorder=4)
        ax.add_patch(arrow1)
        arrows.append(arrow1)
        ax.text(-0.65, -0.5, "SLIDING", ha='center', fontsize=10, 
               fontweight='bold', color='blue', zorder=5)
        
        arrow2 = FancyArrowPatch((0.5, 0.4), (0.8, 0.4),
                                arrowstyle='->', mutation_scale=25, 
                                color='blue', linewidth=3, zorder=4)
        ax.add_patch(arrow2)
        arrows.append(arrow2)
        ax.text(0.65, 0.5, "SLIDING", ha='center', fontsize=10, 
               fontweight='bold', color='blue', zorder=5)
        
        # Earthquakes (shaking effect) - more visible
        if abs(offset) > 0.1:
            for i in range(3):
                eq_x = -0.3 + i * 0.3
                eq_y = fault_y
                # Earthquake symbol (concentric circles) - larger
                for r in [0.06, 0.10, 0.14]:
                    eq = Circle((eq_x, eq_y), r, fill=False, 
                               edgecolor='orange', linewidth=3, 
                               alpha=0.7, zorder=4)
                    ax.add_patch(eq)
                    earthquakes.append(eq)
            
            # Label earthquakes
            ax.text(0, fault_y + 0.2, "EARTHQUAKES!", ha='center', fontsize=11,
                   fontweight='bold', color='orange',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.9),
                   zorder=6)
        
        # Boundary label
        ax.text(0, 0.9, "TRANSFORM BOUNDARY", ha='center', fontsize=11,
               fontweight='bold', color='red',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
               zorder=6)
        
        # Store plate references (already stored above)
        pass
    
    # Update info panel
    update_info(boundary, speed)

def update_info(boundary, speed):
    """Update information panel."""
    effects = {
        "Convergent": "• Mountains form\n• Volcanoes\n• Earthquakes",
        "Divergent": "• Rift valleys\n• New crust forms\n• Mid-ocean ridges",
        "Transform": "• Earthquakes\n• Fault lines\n• No volcanoes"
    }
    
    info = (
        f"╔═══════════════════════════╗\n"
        f"║ PLATE TECTONICS           ║\n"
        f"╚═══════════════════════════╝\n\n"
        f"[*] Boundary Type:\n"
        f"  {boundary}\n"
        f"  {BOUNDARY_TYPES[boundary]}\n\n"
        f"[+] Movement Speed:\n"
        f"  {speed:.0f}%\n\n"
        f"[!] Effects:\n"
        f"  {effects[boundary]}\n\n"
        f"[*] How it works:\n"
        f"  Earth's crust is\n"
        f"  divided into plates\n"
        f"  that move slowly.\n"
        f"  Different movements\n"
        f"  create different\n"
        f"  landforms.\n\n"
        f"[+] Try:\n"
        f"  • Change boundary type\n"
        f"  • Adjust speed\n"
        f"  • Watch the effects!"
    )
    info_text.set_text(info)

# -----------------------------
# Controls
# -----------------------------
# Boundary type radio buttons
ax_boundary = plt.axes([0.08, 0.15, 0.25, 0.08])
boundary_radio = RadioButtons(ax_boundary, list(BOUNDARY_TYPES.keys()), 
                              active=0)

# Movement speed slider
ax_speed = plt.axes([0.08, 0.10, 0.25, 0.03])
speed_slider = Slider(ax_speed, "Speed", 0, 100, valinit=50, valstep=5)

# Buttons
ax_animate = plt.axes([0.35, 0.10, 0.10, 0.04])
btn_animate = Button(ax_animate, "Animate")

ax_reset = plt.axes([0.35, 0.15, 0.10, 0.04])
btn_reset = Button(ax_reset, "Reset")

# -----------------------------
# Animation
# -----------------------------
animation = None

def animate(frame):
    """Animation function."""
    if state["animate"]:
        state["time"] += 0.1
        draw_plates()
    return []

# -----------------------------
# Event Handlers
# -----------------------------
def on_boundary_change(label):
    """Handle boundary type change."""
    state["boundary_type"] = label
    state["time"] = 0.0
    draw_plates()

def on_speed_change(val):
    """Handle speed slider change."""
    state["movement_speed"] = val
    draw_plates()

def on_animate(_):
    """Toggle animation."""
    global animation
    state["animate"] = not state["animate"]
    if state["animate"]:
        btn_animate.label.set_text("Stop")
        if animation is None:
            animation = FuncAnimation(fig, animate, interval=50, 
                                     blit=False, cache_frame_data=False)
    else:
        btn_animate.label.set_text("Animate")
        if animation is not None:
            animation.event_source.stop()
            animation = None
    fig.canvas.draw_idle()

def on_reset(_):
    """Reset to initial state."""
    global animation
    state["time"] = 0.0
    state["animate"] = False
    if animation is not None:
        try:
            animation.event_source.stop()
        except AttributeError:
            pass
        animation = None
    btn_animate.label.set_text("Animate")
    draw_plates()

# Wire up events
boundary_radio.on_clicked(on_boundary_change)
speed_slider.on_changed(on_speed_change)
btn_animate.on_clicked(on_animate)
btn_reset.on_clicked(on_reset)

# Initial visualization
draw_plates()
plt.show()

