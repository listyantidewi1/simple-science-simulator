import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches

# -----------------------------
# Chemical Reactions Simulator
# For Junior High School Chemistry
# -----------------------------

# -----------------------------
# State Management
# -----------------------------
state = {
    "reaction_type": "Combustion",
    "animation_progress": 0.0,
    "is_animating": False,
    "speed": 50
}

# -----------------------------
# Reaction Definitions
# -----------------------------
REACTIONS = {
    "Combustion": {
        "reactants": [
            {"formula": "CH₄", "name": "Methane", "atoms": [("C", 1), ("H", 4)], "color": "#4CAF50"},
            {"formula": "O₂", "name": "Oxygen", "atoms": [("O", 2)], "color": "#2196F3", "count": 2}
        ],
        "products": [
            {"formula": "CO₂", "name": "Carbon Dioxide", "atoms": [("C", 1), ("O", 2)], "color": "#9E9E9E"},
            {"formula": "H₂O", "name": "Water", "atoms": [("H", 2), ("O", 1)], "color": "#03A9F4", "count": 2}
        ],
        "equation": "CH₄ + 2O₂ → CO₂ + 2H₂O",
        "description": "Combustion: Methane burns with oxygen to produce carbon dioxide and water."
    },
    "Acid-Base": {
        "reactants": [
            {"formula": "HCl", "name": "Hydrochloric Acid", "atoms": [("H", 1), ("Cl", 1)], "color": "#F44336"},
            {"formula": "NaOH", "name": "Sodium Hydroxide", "atoms": [("Na", 1), ("O", 1), ("H", 1)], "color": "#FF9800"}
        ],
        "products": [
            {"formula": "NaCl", "name": "Sodium Chloride", "atoms": [("Na", 1), ("Cl", 1)], "color": "#FFEB3B"},
            {"formula": "H₂O", "name": "Water", "atoms": [("H", 2), ("O", 1)], "color": "#03A9F4"}
        ],
        "equation": "HCl + NaOH → NaCl + H₂O",
        "description": "Neutralization: Acid and base react to form salt and water."
    },
    "Synthesis": {
        "reactants": [
            {"formula": "H₂", "name": "Hydrogen", "atoms": [("H", 2)], "color": "#E91E63", "count": 2},
            {"formula": "O₂", "name": "Oxygen", "atoms": [("O", 2)], "color": "#2196F3"}
        ],
        "products": [
            {"formula": "H₂O", "name": "Water", "atoms": [("H", 2), ("O", 1)], "color": "#03A9F4", "count": 2}
        ],
        "equation": "2H₂ + O₂ → 2H₂O",
        "description": "Synthesis: Hydrogen and oxygen combine to form water."
    }
}

# Atom colors
ATOM_COLORS = {
    "H": "#FFFFFF",  # White
    "C": "#000000",  # Black
    "O": "#FF0000",  # Red
    "Cl": "#00FF00", # Green
    "Na": "#FFA500"  # Orange
}

# -----------------------------
# Figure Setup
# -----------------------------
fig = plt.figure(figsize=(16, 10))
fig.suptitle("Chemical Reactions Simulator", fontsize=16, fontweight='bold')

# Main reaction area
ax = plt.axes([0.05, 0.15, 0.65, 0.75])
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-1.6, 1.2)
ax.set_aspect('equal')
ax.axis('off')
ax.set_facecolor('#F5F5F5')

# Info panel
ax_info = plt.axes([0.72, 0.15, 0.26, 0.75])
ax_info.axis('off')
info_text = ax_info.text(
    0.05, 0.98, "",
    transform=ax_info.transAxes,
    va="top",
    ha="left",
    fontsize=10,
    family='monospace',
    bbox=dict(boxstyle="round,pad=1.0", facecolor="#ffffff", alpha=0.95, 
             edgecolor="#1976d2", linewidth=2)
)

# Controls
ax_radio = plt.axes([0.05, 0.05, 0.3, 0.08])
reaction_radio = RadioButtons(ax_radio, list(REACTIONS.keys()), active=0)

ax_speed = plt.axes([0.4, 0.05, 0.2, 0.03])
speed_slider = Slider(ax_speed, 'Speed', 10, 100, valinit=50, valstep=10)

ax_animate = plt.axes([0.65, 0.05, 0.1, 0.04])
btn_animate = Button(ax_animate, 'Animate')

ax_reset = plt.axes([0.77, 0.05, 0.1, 0.04])
btn_reset = Button(ax_reset, 'Reset')

# -----------------------------
# Visualization Variables
# -----------------------------
molecule_patches = []
atom_patches = []
bond_lines = []
text_elements = []  # Track all text elements (atom labels, molecule labels)
arrow = None
equation_text = None

# -----------------------------
# Helper Functions
# -----------------------------
def draw_atom(center, atom_type, radius=0.15, zorder=3, alpha=1.0):
    """Draw a single atom."""
    color = ATOM_COLORS.get(atom_type, "#CCCCCC")
    circle = Circle(center, radius, facecolor=color, edgecolor='black', 
                   linewidth=2, zorder=zorder, alpha=alpha)
    ax.add_patch(circle)
    # Add atom label
    text = ax.text(center[0], center[1], atom_type, ha='center', va='center',
           fontsize=10, fontweight='bold', zorder=zorder+1, alpha=alpha, color='white' if atom_type == 'C' else 'black')
    text_elements.append(text)
    return circle

def draw_bond(start, end, zorder=2, alpha=1.0, linewidth=2):
    """Draw a bond line between two atoms."""
    from matplotlib.lines import Line2D
    line = Line2D([start[0], end[0]], [start[1], end[1]], 
                 color='black', linewidth=int(linewidth), zorder=zorder, alpha=alpha)
    ax.add_line(line)
    return line

def draw_molecule(center, molecule, scale=1.0, zorder=2, alpha=1.0):
    """Draw a molecule with its atoms."""
    patches = []
    atoms = molecule["atoms"]
    color = molecule["color"]
    formula = molecule["formula"]
    # Note: bond_lines are managed globally, but we'll track them per molecule call
    
    # Special handling for common molecules with proper shapes
    if formula == "CH₄":
        # Methane - tetrahedral (C in center, 4 H around)
        c_center = center
        patches.append(draw_atom(c_center, "C", radius=0.18*scale, zorder=zorder, alpha=alpha))
        # 4 H atoms in tetrahedral arrangement
        h_radius = 0.3 * scale
        angles = [np.pi/2, np.pi/2 + 2*np.pi/3, np.pi/2 + 4*np.pi/3, -np.pi/2]
        h_positions = []
        for angle in angles:
            h_x = c_center[0] + h_radius * np.cos(angle)
            h_y = c_center[1] + h_radius * np.sin(angle)
            h_pos = (h_x, h_y)
            h_positions.append(h_pos)
            patches.append(draw_atom(h_pos, "H", radius=0.12*scale, zorder=zorder, alpha=alpha))
        # Draw bonds from C to each H
        for h_pos in h_positions:
            bond_lines.append(draw_bond(c_center, h_pos, zorder=zorder-1, alpha=alpha))
    elif formula == "CO₂":
        # Carbon dioxide - linear (O-C-O)
        offset = 0.25 * scale
        o1_pos = (center[0] - offset, center[1])
        c_pos = center
        o2_pos = (center[0] + offset, center[1])
        patches.append(draw_atom(o1_pos, "O", radius=0.15*scale, zorder=zorder, alpha=alpha))
        patches.append(draw_atom(c_pos, "C", radius=0.15*scale, zorder=zorder, alpha=alpha))
        patches.append(draw_atom(o2_pos, "O", radius=0.15*scale, zorder=zorder, alpha=alpha))
        # Draw double bonds (two lines for each bond)
        bond_lines.append(draw_bond(o1_pos, c_pos, zorder=zorder-1, alpha=alpha))
        bond_lines.append(draw_bond(c_pos, o2_pos, zorder=zorder-1, alpha=alpha))
        # Draw second line for double bonds (slightly offset)
        offset_line = 0.03 * scale
        bond_lines.append(draw_bond((o1_pos[0], o1_pos[1] + offset_line), 
                                    (c_pos[0], c_pos[1] + offset_line), zorder=zorder-1, alpha=alpha, linewidth=2))
        bond_lines.append(draw_bond((c_pos[0], c_pos[1] + offset_line), 
                                    (o2_pos[0], o2_pos[1] + offset_line), zorder=zorder-1, alpha=alpha, linewidth=2))
    elif formula == "H₂O":
        # Water - bent shape (H-O-H)
        o_center = center
        patches.append(draw_atom(o_center, "O", radius=0.15*scale, zorder=zorder, alpha=alpha))
        # Two H atoms at angle
        h_offset = 0.25 * scale
        angle1 = np.pi/6  # 30 degrees
        h1_pos = (o_center[0] - h_offset*np.cos(angle1), o_center[1] - h_offset*np.sin(angle1))
        h2_pos = (o_center[0] + h_offset*np.cos(angle1), o_center[1] - h_offset*np.sin(angle1))
        patches.append(draw_atom(h1_pos, "H", radius=0.12*scale, zorder=zorder, alpha=alpha))
        patches.append(draw_atom(h2_pos, "H", radius=0.12*scale, zorder=zorder, alpha=alpha))
        # Draw bonds from O to each H
        bond_lines.append(draw_bond(o_center, h1_pos, zorder=zorder-1, alpha=alpha))
        bond_lines.append(draw_bond(o_center, h2_pos, zorder=zorder-1, alpha=alpha))
    elif formula == "HCl":
        # Hydrogen chloride - linear
        offset = 0.2 * scale
        h_pos = (center[0] - offset, center[1])
        cl_pos = (center[0] + offset, center[1])
        patches.append(draw_atom(h_pos, "H", radius=0.12*scale, zorder=zorder, alpha=alpha))
        patches.append(draw_atom(cl_pos, "Cl", radius=0.15*scale, zorder=zorder, alpha=alpha))
        # Draw bond
        bond_lines.append(draw_bond(h_pos, cl_pos, zorder=zorder-1, alpha=alpha))
    elif formula == "NaOH":
        # Sodium hydroxide - Na-O-H
        offset = 0.2 * scale
        na_pos = (center[0] - offset*1.5, center[1])
        o_pos = center
        h_pos = (center[0] + offset*1.5, center[1])
        patches.append(draw_atom(na_pos, "Na", radius=0.15*scale, zorder=zorder, alpha=alpha))
        patches.append(draw_atom(o_pos, "O", radius=0.15*scale, zorder=zorder, alpha=alpha))
        patches.append(draw_atom(h_pos, "H", radius=0.12*scale, zorder=zorder, alpha=alpha))
        # Draw bonds
        bond_lines.append(draw_bond(na_pos, o_pos, zorder=zorder-1, alpha=alpha))
        bond_lines.append(draw_bond(o_pos, h_pos, zorder=zorder-1, alpha=alpha))
    elif formula == "NaCl":
        # Sodium chloride - linear
        offset = 0.2 * scale
        na_pos = (center[0] - offset, center[1])
        cl_pos = (center[0] + offset, center[1])
        patches.append(draw_atom(na_pos, "Na", radius=0.15*scale, zorder=zorder, alpha=alpha))
        patches.append(draw_atom(cl_pos, "Cl", radius=0.15*scale, zorder=zorder, alpha=alpha))
        # Draw bond
        bond_lines.append(draw_bond(na_pos, cl_pos, zorder=zorder-1, alpha=alpha))
    else:
        # Generic molecule drawing
        # Calculate positions for atoms in molecule
        num_atoms = sum(count for _, count in atoms)
        num_atom_types = len(atoms)
        
        if num_atoms == 1:
            # Single atom
            atom_type, count = atoms[0]
            patches.append(draw_atom(center, atom_type, radius=0.15*scale, zorder=zorder, alpha=alpha))
        elif num_atoms == 2:
            if num_atom_types == 1:
                # Two atoms of same type (e.g., O₂) - side by side
                atom_type, count = atoms[0]
                offset = 0.2 * scale
                pos1 = (center[0] - offset, center[1])
                pos2 = (center[0] + offset, center[1])
                patches.append(draw_atom(pos1, atom_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                patches.append(draw_atom(pos2, atom_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                # Draw bond
                bond_lines.append(draw_bond(pos1, pos2, zorder=zorder-1, alpha=alpha))
            else:
                # Two different atoms - side by side
                atom1_type, atom1_count = atoms[0]
                atom2_type, atom2_count = atoms[1]
                offset = 0.2 * scale
                pos1 = (center[0] - offset, center[1])
                pos2 = (center[0] + offset, center[1])
                patches.append(draw_atom(pos1, atom1_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                patches.append(draw_atom(pos2, atom2_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                # Draw bond
                bond_lines.append(draw_bond(pos1, pos2, zorder=zorder-1, alpha=alpha))
        elif num_atoms == 3:
            if num_atom_types == 1:
                # Three atoms of same type - triangular
                atom_type, count = atoms[0]
                offset = 0.2 * scale
                patches.append(draw_atom((center[0], center[1] + offset), atom_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                patches.append(draw_atom((center[0] - offset, center[1] - offset), atom_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                patches.append(draw_atom((center[0] + offset, center[1] - offset), atom_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
            elif num_atom_types == 2:
                # Two types, three atoms - triangular with central atom
                atom1_type, atom1_count = atoms[0]
                atom2_type, atom2_count = atoms[1]
                offset = 0.2 * scale
                # Central atom (usually the one with count 1)
                if atom1_count == 1:
                    patches.append(draw_atom(center, atom1_type, radius=0.15*scale, zorder=zorder, alpha=alpha))
                    patches.append(draw_atom((center[0] - offset, center[1]), atom2_type, 
                                             radius=0.15*scale, zorder=zorder, alpha=alpha))
                    patches.append(draw_atom((center[0] + offset, center[1]), atom2_type, 
                                             radius=0.15*scale, zorder=zorder, alpha=alpha))
                else:
                    patches.append(draw_atom(center, atom2_type, radius=0.15*scale, zorder=zorder, alpha=alpha))
                    patches.append(draw_atom((center[0] - offset, center[1]), atom1_type, 
                                             radius=0.15*scale, zorder=zorder, alpha=alpha))
                    patches.append(draw_atom((center[0] + offset, center[1]), atom1_type, 
                                             radius=0.15*scale, zorder=zorder, alpha=alpha))
            else:
                # Three different atoms - triangular
                atom1_type, atom1_count = atoms[0]
                atom2_type, atom2_count = atoms[1]
                atom3_type, atom3_count = atoms[2]
                offset = 0.2 * scale
                patches.append(draw_atom((center[0], center[1] + offset), atom1_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                patches.append(draw_atom((center[0] - offset, center[1] - offset), atom2_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
                patches.append(draw_atom((center[0] + offset, center[1] - offset), atom3_type, 
                                         radius=0.15*scale, zorder=zorder, alpha=alpha))
        else:
            # Multiple atoms (num_atoms > 3) - arrange in a circle
            angle_step = 2 * np.pi / num_atoms
            radius_offset = 0.25 * scale
            idx = 0
            for atom_type, count in atoms:
                for _ in range(count):
                    angle = idx * angle_step
                    x = center[0] + radius_offset * np.cos(angle)
                    y = center[1] + radius_offset * np.sin(angle)
                    patches.append(draw_atom((x, y), atom_type, radius=0.15*scale, zorder=zorder, alpha=alpha))
                    idx += 1
    
    # Add molecule label - position below molecule with better spacing
    label_text = ax.text(center[0], center[1] - 0.5*scale, formula, ha='center', va='top',
           fontsize=11, fontweight='bold', color=color, zorder=zorder+1, alpha=alpha)
    text_elements.append(label_text)
    
    return patches

def clear_visualization():
    """Clear all visual elements."""
    global molecule_patches, atom_patches, bond_lines, text_elements, arrow, equation_text
    
    # Clear molecules (patches)
    for patch_list in molecule_patches:
        if isinstance(patch_list, list):
            for patch in patch_list:
                try:
                    patch.remove()
                except (ValueError, AttributeError):
                    pass
        else:
            try:
                patch_list.remove()
            except (ValueError, AttributeError):
                pass
    molecule_patches = []
    atom_patches = []
    
    # Clear bonds
    for bond in bond_lines:
        try:
            bond.remove()
        except (ValueError, AttributeError):
            pass
    bond_lines = []
    
    # Clear all text elements (atom labels, molecule labels)
    for text in text_elements:
        try:
            text.remove()
        except (ValueError, AttributeError):
            pass
    text_elements = []
    
    # Clear arrow
    if arrow is not None:
        try:
            arrow.remove()
        except (ValueError, AttributeError):
            pass
        arrow = None
    
    # Clear equation text
    if equation_text is not None:
        try:
            equation_text.remove()
        except (ValueError, AttributeError):
            pass
        equation_text = None

def draw_reaction():
    """Draw the chemical reaction visualization."""
    clear_visualization()
    
    reaction = REACTIONS[state["reaction_type"]]
    progress = state["animation_progress"]
    
    # Calculate total number of reactant molecules (including counts)
    reactants = reaction["reactants"]
    total_reactant_molecules = sum(reactant.get("count", 1) for reactant in reactants)
    
    # Calculate total number of product molecules (including counts)
    products = reaction["products"]
    total_product_molecules = sum(product.get("count", 1) for product in products)
    
    # Better spacing: distribute molecules evenly in vertical space
    # Use more vertical space (from 0.8 to -0.8) for better separation
    reactant_y_start = 0.8
    reactant_y_end = -0.3
    product_y_start = 0.8
    product_y_end = -0.3
    
    # Draw reactants on the left
    molecule_idx = 0
    for i, reactant in enumerate(reactants):
        count = reactant.get("count", 1)
        # Smooth movement: start at left, move toward center
        x_pos = -1.4 + progress * 0.4
        
        # Fade out reactants as they move
        alpha = max(0.3, 1.0 - progress * 0.7)
        
        for j in range(count):
            # Better vertical distribution
            if total_reactant_molecules > 1:
                y_pos = reactant_y_start - (molecule_idx / (total_reactant_molecules - 1)) * (reactant_y_start - reactant_y_end)
            else:
                y_pos = (reactant_y_start + reactant_y_end) / 2
            
            patches = draw_molecule((x_pos, y_pos), reactant, scale=0.75, alpha=alpha)
            molecule_patches.append(patches)
            molecule_idx += 1
    
    # Draw arrow - appears as reaction progresses
    arrow_x = -0.1 + progress * 0.2
    global arrow
    if progress > 0.1:
        arrow_alpha = min(1.0, (progress - 0.1) / 0.3)
        arrow = FancyArrowPatch((arrow_x - 0.4, 0.25), (arrow_x + 0.4, 0.25),
                               arrowstyle='->', mutation_scale=30, 
                               color='black', linewidth=3, zorder=4, alpha=arrow_alpha)
        ax.add_patch(arrow)
    
    # Draw products on the right - fade in as reaction progresses
    molecule_idx = 0
    for i, product in enumerate(products):
        count = product.get("count", 1)
        # Start from center, move to right
        x_pos = 0.3 + (1 - progress) * 0.3 + progress * 0.5
        
        # Fade in products as reaction progresses
        alpha = min(1.0, max(0.0, (progress - 0.3) / 0.4))
        
        for j in range(count):
            # Better vertical distribution
            if total_product_molecules > 1:
                y_pos = product_y_start - (molecule_idx / (total_product_molecules - 1)) * (product_y_start - product_y_end)
            else:
                y_pos = (product_y_start + product_y_end) / 2
            
            patches = draw_molecule((x_pos, y_pos), product, scale=0.75, alpha=alpha)
            molecule_patches.append(patches)
            molecule_idx += 1
    
    # Draw equation - position it lower to avoid overlap
    global equation_text
    equation_text = ax.text(0, -1.35, reaction["equation"], ha='center', va='center',
                           fontsize=14, fontweight='bold', zorder=5,
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.8))
    
    # Update info panel
    update_info_panel(reaction)

def update_info_panel(reaction):
    """Update the information panel."""
    info = f"""
╔═══════════════════════════════╗
║  CHEMICAL REACTION INFO       ║
╚═══════════════════════════════╝

Reaction Type: {state["reaction_type"]}

Equation:
{reaction["equation"]}

Description:
{reaction["description"]}

Reactants:
"""
    for reactant in reaction["reactants"]:
        count = reactant.get("count", 1)
        count_str = f"{count}× " if count > 1 else ""
        info += f"  {count_str}{reactant['formula']} - {reactant['name']}\n"
    
    info += "\nProducts:\n"
    for product in reaction["products"]:
        count = product.get("count", 1)
        count_str = f"{count}× " if count > 1 else ""
        info += f"  {count_str}{product['formula']} - {product['name']}\n"
    
    info += f"\nProgress: {int(state['animation_progress'] * 100)}%"
    
    info_text.set_text(info)

# -----------------------------
# Animation
# -----------------------------
animation = None

def animate(frame):
    """Animation function."""
    if state["is_animating"]:
        state["animation_progress"] += 0.02 * (state["speed"] / 50)
        if state["animation_progress"] >= 1.0:
            state["animation_progress"] = 1.0
            state["is_animating"] = False
            btn_animate.label.set_text("Animate")
            if animation is not None:
                try:
                    animation.event_source.stop()
                except AttributeError:
                    pass
        draw_reaction()
    return []

# -----------------------------
# Event Handlers
# -----------------------------
def on_reaction_change(label):
    """Handle reaction type change."""
    state["reaction_type"] = label
    state["animation_progress"] = 0.0
    state["is_animating"] = False
    draw_reaction()

def on_speed_change(val):
    """Handle speed slider change."""
    state["speed"] = val

def on_animate(_):
    """Toggle animation."""
    global animation
    state["is_animating"] = not state["is_animating"]
    
    if state["is_animating"]:
        btn_animate.label.set_text("Stop")
        if animation is None:
            animation = FuncAnimation(fig, animate, interval=50, 
                                     blit=False, cache_frame_data=False)
    else:
        btn_animate.label.set_text("Animate")
        if animation is not None:
            try:
                animation.event_source.stop()
            except AttributeError:
                pass
            animation = None
    fig.canvas.draw_idle()

def on_reset(_):
    """Reset to initial state."""
    global animation
    state["animation_progress"] = 0.0
    state["is_animating"] = False
    if animation is not None:
        try:
            animation.event_source.stop()
        except AttributeError:
            pass
        animation = None
    btn_animate.label.set_text("Animate")
    clear_visualization()
    draw_reaction()
    fig.canvas.draw_idle()

# Wire up events
reaction_radio.on_clicked(on_reaction_change)
speed_slider.on_changed(on_speed_change)
btn_animate.on_clicked(on_animate)
btn_reset.on_clicked(on_reset)

# Initial visualization
draw_reaction()
plt.show()

