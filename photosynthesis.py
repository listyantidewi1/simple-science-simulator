import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Circle, Rectangle, Polygon, FancyArrowPatch, Arc, RegularPolygon
import matplotlib.patches as mpatches

# -----------------------------
# Photosynthesis Simulator
# For Junior High School Biology
# -----------------------------

# State
state = {
    "sunlight": 50,    # Sunlight intensity (0-100)
    "co2": 50,         # CO2 level (0-100)
    "water": 50,       # Water level (0-100)
    "temperature": 25  # Temperature in Celsius (10-40)
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(14, 9))
plt.subplots_adjust(left=0.08, bottom=0.25, right=0.68, top=0.95)

# Main visualization axes
ax = plt.axes([0.08, 0.30, 0.58, 0.65])
ax.set_title("Photosynthesis Simulator - Junior High Biology", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.axis('off')
ax.set_facecolor('#e8f5e9')  # Light green background

# Visual elements
sun = None
sun_rays = []
plant_pot = None
plant_stem = None
plant_leaves = []
co2_molecules = []
water_droplets = []
oxygen_bubbles = []
glucose_molecules = []
arrows = []
reaction_text = None

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
             edgecolor="#4caf50", linewidth=2)
)

# -----------------------------
# Photosynthesis Functions
# -----------------------------
def calculate_photosynthesis_rate(sunlight, co2, water, temp):
    """Calculate photosynthesis rate based on inputs."""
    # Optimal temperature around 25°C
    temp_factor = 1.0 - abs(temp - 25) / 30.0
    temp_factor = max(0.1, temp_factor)
    
    # Rate depends on limiting factor (minimum of inputs)
    limiting_factor = min(sunlight, co2, water) / 100.0
    
    # Photosynthesis rate
    rate = limiting_factor * temp_factor * 100
    
    return max(0, min(100, rate))

def calculate_outputs(rate):
    """Calculate glucose and oxygen outputs."""
    # Simplified: 6 CO2 + 6 H2O → C6H12O6 + 6 O2
    glucose = rate * 0.1  # Glucose production (simplified)
    oxygen = rate * 0.15  # Oxygen production (simplified)
    return glucose, oxygen

# -----------------------------
# Visualization Functions
# -----------------------------
def clear_visualization():
    """Clear all visual elements."""
    global sun, sun_rays, plant_pot, plant_stem, plant_leaves
    global co2_molecules, water_droplets, oxygen_bubbles, glucose_molecules
    global arrows, reaction_text
    
    # Clear sun
    if sun is not None:
        try:
            sun.remove()
        except (ValueError, AttributeError):
            pass
        sun = None
    
    for ray in sun_rays:
        try:
            ray.remove()
        except (ValueError, AttributeError):
            pass
    sun_rays = []
    
    # Clear plant
    if plant_pot is not None:
        if isinstance(plant_pot, list):
            for patch in plant_pot:
                try:
                    patch.remove()
                except (ValueError, AttributeError):
                    pass
        else:
            try:
                plant_pot.remove()
            except (ValueError, AttributeError):
                pass
        plant_pot = None
    
    if plant_stem is not None:
        try:
            plant_stem.remove()
        except (ValueError, AttributeError):
            pass
        plant_stem = None
    
    for leaf in plant_leaves:
        try:
            leaf.remove()
        except (ValueError, AttributeError):
            pass
    plant_leaves = []
    
    # Clear molecules
    for mol in co2_molecules:
        try:
            mol.remove()
        except (ValueError, AttributeError):
            pass
    co2_molecules = []
    
    for drop in water_droplets:
        try:
            drop.remove()
        except (ValueError, AttributeError):
            pass
    water_droplets = []
    
    for bubble in oxygen_bubbles:
        try:
            bubble.remove()
        except (ValueError, AttributeError):
            pass
    oxygen_bubbles = []
    
    for glucose in glucose_molecules:
        try:
            glucose.remove()
        except (ValueError, AttributeError):
            pass
    glucose_molecules = []
    
    for arrow in arrows:
        try:
            arrow.remove()
        except (ValueError, AttributeError):
            pass
    arrows = []
    
    if reaction_text is not None:
        try:
            reaction_text.remove()
        except (ValueError, AttributeError):
            pass
        reaction_text = None

def draw_photosynthesis():
    """Draw the photosynthesis visualization."""
    clear_visualization()
    
    sunlight = state["sunlight"]
    co2_level = state["co2"]
    water_level = state["water"]
    temp = state["temperature"]
    
    # Calculate photosynthesis rate
    rate = calculate_photosynthesis_rate(sunlight, co2_level, water_level, temp)
    glucose, oxygen = calculate_outputs(rate)
    
    # Draw sun (top center)
    global sun
    sun = Circle((0, 0.7), 0.15, fill=True, facecolor='#ffeb3b', 
                 edgecolor='#ffc107', lw=2, zorder=5)
    ax.add_patch(sun)
    
    # Sun rays (intensity based on sunlight level)
    num_rays = int(sunlight / 10) + 3
    for i in range(num_rays):
        angle = 2 * np.pi * i / num_rays
        x1 = 0.15 * np.cos(angle)
        y1 = 0.7 + 0.15 * np.sin(angle)
        x2 = 0.25 * np.cos(angle)
        y2 = 0.7 + 0.25 * np.sin(angle)
        ray = plt.Line2D([x1, x2], [y1, y2], color='#ffeb3b', 
                        linewidth=2, alpha=0.6, zorder=4)
        ax.add_line(ray)
        sun_rays.append(ray)
    
    # Draw plant pot (bottom center)
    global plant_pot
    pot_width = 0.3
    pot_height = 0.15
    pot_x = -pot_width / 2
    pot_y = -0.9
    
    # Pot body
    pot_body = Rectangle((pot_x, pot_y), pot_width, pot_height * 0.7,
                        facecolor='#8d6e63', edgecolor='#5d4037', lw=2, zorder=2)
    ax.add_patch(pot_body)
    
    # Pot rim
    pot_rim = Rectangle((pot_x - 0.02, pot_y + pot_height * 0.7), 
                       pot_width + 0.04, pot_height * 0.3,
                       facecolor='#a1887f', edgecolor='#5d4037', lw=2, zorder=2)
    ax.add_patch(pot_rim)
    plant_pot = [pot_body, pot_rim]
    
    # Draw plant stem
    global plant_stem
    stem_height = 0.4 + (rate / 100) * 0.2  # Stem grows with photosynthesis
    stem = Rectangle((0, pot_y + pot_height), 0.05, stem_height,
                    facecolor='#4caf50', edgecolor='#2e7d32', lw=2, zorder=3)
    ax.add_patch(stem)
    plant_stem = stem
    
    # Draw leaves (size based on photosynthesis rate)
    leaf_size = 0.15 + (rate / 100) * 0.1
    
    # Left leaf
    leaf1_points = [
        (0, pot_y + pot_height + stem_height * 0.7),
        (-leaf_size, pot_y + pot_height + stem_height * 0.7 + leaf_size * 0.5),
        (-leaf_size * 0.5, pot_y + pot_height + stem_height * 0.7 + leaf_size)
    ]
    leaf1 = Polygon(leaf1_points, closed=True, facecolor='#66bb6a', 
                   edgecolor='#2e7d32', lw=2, zorder=3)
    ax.add_patch(leaf1)
    plant_leaves.append(leaf1)
    
    # Right leaf
    leaf2_points = [
        (0, pot_y + pot_height + stem_height * 0.7),
        (leaf_size, pot_y + pot_height + stem_height * 0.7 + leaf_size * 0.5),
        (leaf_size * 0.5, pot_y + pot_height + stem_height * 0.7 + leaf_size)
    ]
    leaf2 = Polygon(leaf2_points, closed=True, facecolor='#66bb6a', 
                   edgecolor='#2e7d32', lw=2, zorder=3)
    ax.add_patch(leaf2)
    plant_leaves.append(leaf2)
    
    # Draw CO2 molecules (coming from air)
    num_co2 = int(co2_level / 15) + 1
    for i in range(num_co2):
        x = -0.6 + (i % 3) * 0.3
        y = 0.3 + (i // 3) * 0.2
        # CO2 molecule (C with 2 O atoms)
        c_atom = Circle((x, y), 0.04, facecolor='black', zorder=4)
        o1 = Circle((x - 0.06, y), 0.03, facecolor='red', zorder=4)
        o2 = Circle((x + 0.06, y), 0.03, facecolor='red', zorder=4)
        ax.add_patch(c_atom)
        ax.add_patch(o1)
        ax.add_patch(o2)
        co2_molecules.extend([c_atom, o1, o2])
        
        # Arrow pointing to leaf
        arrow = FancyArrowPatch((x, y), (0, pot_y + pot_height + stem_height * 0.7),
                               arrowstyle='->', mutation_scale=15, 
                               color='gray', alpha=0.6, linewidth=1.5, zorder=3)
        ax.add_patch(arrow)
        arrows.append(arrow)
    
    # Draw water droplets (from roots)
    num_water = int(water_level / 15) + 1
    for i in range(num_water):
        x = -0.3 + (i % 2) * 0.2
        y = -0.5 - (i // 2) * 0.15
        # Water droplet (H2O)
        h1 = Circle((x - 0.03, y), 0.025, facecolor='lightblue', zorder=4)
        h2 = Circle((x + 0.03, y), 0.025, facecolor='lightblue', zorder=4)
        o = Circle((x, y + 0.02), 0.03, facecolor='blue', zorder=4)
        ax.add_patch(h1)
        ax.add_patch(h2)
        ax.add_patch(o)
        water_droplets.extend([h1, h2, o])
        
        # Arrow pointing up
        arrow = FancyArrowPatch((x, y), (0, pot_y + pot_height),
                               arrowstyle='->', mutation_scale=15, 
                               color='blue', alpha=0.6, linewidth=1.5, zorder=3)
        ax.add_patch(arrow)
        arrows.append(arrow)
    
    # Draw oxygen bubbles (output)
    num_oxygen = int(oxygen / 10) + 1
    for i in range(min(num_oxygen, 8)):
        angle = 2 * np.pi * i / 8
        x = 0.4 + 0.2 * np.cos(angle)
        y = 0.2 + 0.2 * np.sin(angle)
        # Oxygen molecule (O2)
        o1 = Circle((x - 0.02, y), 0.03, facecolor='lightblue', 
                   edgecolor='blue', lw=1, zorder=4)
        o2 = Circle((x + 0.02, y), 0.03, facecolor='lightblue', 
                   edgecolor='blue', lw=1, zorder=4)
        ax.add_patch(o1)
        ax.add_patch(o2)
        oxygen_bubbles.extend([o1, o2])
        
        # Arrow from leaf
        arrow = FancyArrowPatch((0, pot_y + pot_height + stem_height * 0.7), (x, y),
                               arrowstyle='->', mutation_scale=15, 
                               color='lightblue', alpha=0.7, linewidth=2, zorder=3)
        ax.add_patch(arrow)
        arrows.append(arrow)
    
    # Draw glucose molecules (output)
    num_glucose = int(glucose / 15) + 1
    for i in range(min(num_glucose, 5)):
        x = 0.5 + (i % 3) * 0.15
        y = -0.3 - (i // 3) * 0.15
        # Simple glucose representation (hexagon)
        hexagon = RegularPolygon((x, y), 6, radius=0.04, 
                                orientation=0, facecolor='orange', 
                                edgecolor='darkorange', lw=1.5, zorder=4)
        ax.add_patch(hexagon)
        glucose_molecules.append(hexagon)
        
        # Arrow from leaf
        arrow = FancyArrowPatch((0, pot_y + pot_height + stem_height * 0.7), (x, y),
                               arrowstyle='->', mutation_scale=15, 
                               color='orange', alpha=0.7, linewidth=2, zorder=3)
        ax.add_patch(arrow)
        arrows.append(arrow)
    
    # Reaction equation text
    global reaction_text
    reaction_text = ax.text(0, -0.7, 
                           f"6 CO₂ + 6 H₂O + Light → C₆H₁₂O₆ + 6 O₂",
                           ha='center', va='center', fontsize=11, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", 
                                   alpha=0.9, edgecolor="orange", linewidth=2),
                           zorder=6)
    
    # Update info panel
    update_info(rate, glucose, oxygen, sunlight, co2_level, water_level, temp)

def update_info(rate, glucose, oxygen, sunlight, co2, water, temp):
    """Update information panel."""
    status = "Excellent" if rate > 70 else "Good" if rate > 40 else "Low" if rate > 10 else "Very Low"
    status_color = "green" if rate > 70 else "orange" if rate > 40 else "red"
    
    info = (
        f"╔═══════════════════════════╗\n"
        f"║ PHOTOSYNTHESIS           ║\n"
        f"╚═══════════════════════════╝\n\n"
        f"[*] Status: {status}\n"
        f"    Rate: {rate:.1f}%\n\n"
        f"[+] Inputs:\n"
        f"  Sunlight: {sunlight:.0f}%\n"
        f"  CO₂: {co2:.0f}%\n"
        f"  Water: {water:.0f}%\n"
        f"  Temperature: {temp:.0f}°C\n\n"
        f"[+] Outputs:\n"
        f"  Glucose: {glucose:.2f} units\n"
        f"  Oxygen: {oxygen:.2f} units\n\n"
        f"[!] Process:\n"
        f"  Plants use sunlight,\n"
        f"  CO₂, and water to\n"
        f"  make glucose (food)\n"
        f"  and oxygen.\n\n"
        f"[*] Equation:\n"
        f"  6 CO₂ + 6 H₂O\n"
        f"  + Light →\n"
        f"  C₆H₁₂O₆ + 6 O₂"
    )
    info_text.set_text(info)

# -----------------------------
# Controls
# -----------------------------
# Sunlight slider
ax_sunlight = plt.axes([0.08, 0.20, 0.25, 0.03])
sunlight_slider = Slider(ax_sunlight, "Sunlight", 0, 100, valinit=50, valstep=5)

# CO2 slider
ax_co2 = plt.axes([0.08, 0.15, 0.25, 0.03])
co2_slider = Slider(ax_co2, "CO₂ Level", 0, 100, valinit=50, valstep=5)

# Water slider
ax_water = plt.axes([0.08, 0.10, 0.25, 0.03])
water_slider = Slider(ax_water, "Water", 0, 100, valinit=50, valstep=5)

# Temperature slider
ax_temp = plt.axes([0.35, 0.10, 0.25, 0.03])
temp_slider = Slider(ax_temp, "Temperature (°C)", 10, 40, valinit=25, valstep=1)

# Buttons
ax_reset = plt.axes([0.35, 0.15, 0.10, 0.04])
btn_reset = Button(ax_reset, "Reset")

ax_optimal = plt.axes([0.35, 0.20, 0.15, 0.04])
btn_optimal = Button(ax_optimal, "Optimal")

# -----------------------------
# Event Handlers
# -----------------------------
def on_sunlight_change(val):
    """Handle sunlight slider change."""
    state["sunlight"] = val
    draw_photosynthesis()

def on_co2_change(val):
    """Handle CO2 slider change."""
    state["co2"] = val
    draw_photosynthesis()

def on_water_change(val):
    """Handle water slider change."""
    state["water"] = val
    draw_photosynthesis()

def on_temp_change(val):
    """Handle temperature slider change."""
    state["temperature"] = val
    draw_photosynthesis()

def on_reset(_):
    """Reset to default values."""
    state["sunlight"] = 50
    state["co2"] = 50
    state["water"] = 50
    state["temperature"] = 25
    sunlight_slider.reset()
    co2_slider.reset()
    water_slider.reset()
    temp_slider.reset()
    draw_photosynthesis()

def on_optimal(_):
    """Set optimal conditions."""
    state["sunlight"] = 80
    state["co2"] = 70
    state["water"] = 75
    state["temperature"] = 25
    sunlight_slider.set_val(80)
    co2_slider.set_val(70)
    water_slider.set_val(75)
    temp_slider.set_val(25)
    draw_photosynthesis()

# Wire up events
sunlight_slider.on_changed(on_sunlight_change)
co2_slider.on_changed(on_co2_change)
water_slider.on_changed(on_water_change)
temp_slider.on_changed(on_temp_change)
btn_reset.on_clicked(on_reset)
btn_optimal.on_clicked(on_optimal)

# Initial visualization
draw_photosynthesis()
plt.show()

