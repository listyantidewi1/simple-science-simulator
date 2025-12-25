import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, FancyBboxPatch, Polygon
from matplotlib import cm

# -----------------------------
# Cell Division (Mitosis) Simulator
# -----------------------------

# Stages of mitosis
STAGES = {
    "Interphase": 0,
    "Prophase": 1,
    "Metaphase": 2,
    "Anaphase": 3,
    "Telophase": 4,
    "Cytokinesis": 5
}

STAGE_DESCRIPTIONS = {
    "Interphase": "Cell grows, DNA replicates. Chromosomes are not visible.",
    "Prophase": "Chromosomes condense, nuclear envelope breaks down, spindle forms.",
    "Metaphase": "Chromosomes align at the cell equator (metaphase plate).",
    "Anaphase": "Sister chromatids separate and move to opposite poles.",
    "Telophase": "Chromosomes decondense, nuclear envelopes reform, cell begins to divide.",
    "Cytokinesis": "Cell membrane pinches inward, forming two daughter cells."
}

# -----------------------------
# Initial parameters
# -----------------------------
num_chromosomes = 4  # Number of chromosome pairs (diploid)
cell_radius = 1.0
nucleus_radius = 0.6

# State
state = {
    "stage": 0,  # Current stage index
    "time": 0.0,  # Animation time within stage
    "animate": False,
    "speed": 1.0
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(14, 8))
plt.subplots_adjust(left=0.08, bottom=0.25, right=0.68, top=0.95)

# Main plot axes
ax = plt.subplot(1, 1, 1)
ax.set_title("Cell Division (Mitosis) Simulator", fontsize=14, fontweight='bold')
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-1.8, 1.8)
ax.axis('off')

# Cell membrane (will be updated)
cell_membrane = None
nucleus = None
chromosomes = []
spindle_fibers = []
centrosomes = []
text_elements = []  # Track text elements to remove them

# Stage label
stage_label = ax.text(0, -1.6, "", ha='center', va='top', fontsize=14, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.8))

# Info text panel - positioned on the right side
ax_text = plt.axes([0.70, 0.25, 0.29, 0.70])
ax_text.axis('off')
# Set margins to prevent clipping
ax_text.set_xlim(0, 1)
ax_text.set_ylim(0, 1)
info_text = ax_text.text(
    0.02, 0.98, "",
    transform=ax_text.transAxes,
    va="top",
    ha="left",
    fontsize=9,
    family='monospace',
    bbox=dict(boxstyle="round,pad=0.8", facecolor="white", alpha=0.95, edgecolor="gray", linewidth=1.5)
)

# -----------------------------
# Chromosome class
# -----------------------------
class Chromosome:
    def __init__(self, center, angle, length=0.15, width=0.08, color='blue', pair_id=0):
        self.center = np.array(center)
        self.angle = angle
        self.length = length
        self.width = width
        self.color = color
        self.pair_id = pair_id
        self.is_separated = False
        self.patch = None
        
    def draw(self, ax):
        """Draw chromosome as an X shape (two chromatids)."""
        if self.patch is not None:
            if isinstance(self.patch, list):
                for p in self.patch:
                    p.remove()
            else:
                self.patch.remove()
        
        # Create X shape for chromosome
        cx, cy = self.center
        
        # Two chromatids forming X
        if not self.is_separated:
            # Draw as X (two chromatids joined)
            points1 = [
                [cx - self.length/2 * np.cos(self.angle), cy - self.length/2 * np.sin(self.angle)],
                [cx + self.length/2 * np.cos(self.angle), cy + self.length/2 * np.sin(self.angle)],
                [cx + self.length/2 * np.cos(self.angle) + self.width * np.sin(self.angle), 
                 cy + self.length/2 * np.sin(self.angle) - self.width * np.cos(self.angle)],
                [cx - self.length/2 * np.cos(self.angle) + self.width * np.sin(self.angle), 
                 cy - self.length/2 * np.sin(self.angle) - self.width * np.cos(self.angle)]
            ]
            points2 = [
                [cx - self.length/2 * np.cos(self.angle), cy - self.length/2 * np.sin(self.angle)],
                [cx + self.length/2 * np.cos(self.angle), cy + self.length/2 * np.sin(self.angle)],
                [cx + self.length/2 * np.cos(self.angle) - self.width * np.sin(self.angle), 
                 cy + self.length/2 * np.sin(self.angle) + self.width * np.cos(self.angle)],
                [cx - self.length/2 * np.cos(self.angle) - self.width * np.sin(self.angle), 
                 cy - self.length/2 * np.sin(self.angle) + self.width * np.cos(self.angle)]
            ]
            poly1 = Polygon(points1, closed=True, facecolor=self.color, edgecolor='black', lw=1, zorder=5)
            poly2 = Polygon(points2, closed=True, facecolor=self.color, edgecolor='black', lw=1, zorder=5)
            ax.add_patch(poly1)
            ax.add_patch(poly2)
            self.patch = [poly1, poly2]
        else:
            # Draw as separated chromatids (two lines)
            offset = self.width
            p1 = [cx - self.length/2 * np.cos(self.angle) + offset * np.sin(self.angle),
                  cy - self.length/2 * np.sin(self.angle) - offset * np.cos(self.angle)]
            p2 = [cx + self.length/2 * np.cos(self.angle) + offset * np.sin(self.angle),
                  cy + self.length/2 * np.sin(self.angle) - offset * np.cos(self.angle)]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=self.color, lw=4, zorder=5)
            
            p3 = [cx - self.length/2 * np.cos(self.angle) - offset * np.sin(self.angle),
                  cy - self.length/2 * np.sin(self.angle) + offset * np.cos(self.angle)]
            p4 = [cx + self.length/2 * np.cos(self.angle) - offset * np.sin(self.angle),
                  cy + self.length/2 * np.sin(self.angle) + offset * np.cos(self.angle)]
            ax.plot([p3[0], p4[0]], [p3[1], p4[1]], color=self.color, lw=4, zorder=5)
            self.patch = None

# -----------------------------
# Helper functions
# -----------------------------
def clear_elements():
    """Clear all visual elements."""
    global cell_membrane, nucleus, chromosomes, spindle_fibers, centrosomes, text_elements
    
    if cell_membrane is not None:
        if isinstance(cell_membrane, list):
            for cm in cell_membrane:
                cm.remove()
        else:
            cell_membrane.remove()
        cell_membrane = None
    
    if nucleus is not None:
        if isinstance(nucleus, list):
            for n in nucleus:
                n.remove()
        else:
            nucleus.remove()
        nucleus = None
    
    for chrom in chromosomes:
        if chrom.patch is not None:
            if isinstance(chrom.patch, list):
                for p in chrom.patch:
                    p.remove()
            else:
                chrom.patch.remove()
    chromosomes = []
    
    for fiber in spindle_fibers:
        fiber.remove()
    spindle_fibers = []
    
    for centrosome in centrosomes:
        centrosome.remove()
    centrosomes = []
    
    # Remove text elements
    for text in text_elements:
        text.remove()
    text_elements = []

def get_stage_name(index):
    """Get stage name from index."""
    for name, idx in STAGES.items():
        if idx == index:
            return name
    return "Unknown"

def update_visualization():
    """Update the visualization based on current stage."""
    global cell_membrane, nucleus, chromosomes, spindle_fibers, centrosomes
    
    clear_elements()
    
    stage_idx = state["stage"]
    stage_name = get_stage_name(stage_idx)
    time = state["time"]
    
    # Colors for chromosomes (different pairs)
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown']
    
    # Interphase
    if stage_idx == 0:
        # Cell membrane
        cell_membrane = Circle((0, 0), cell_radius, fill=False, edgecolor='black', lw=3, zorder=1)
        ax.add_patch(cell_membrane)
        
        # Nucleus (large, chromosomes not visible)
        nucleus = Circle((0, 0), nucleus_radius, fill=True, facecolor='lightblue', 
                        edgecolor='darkblue', lw=2, alpha=0.5, zorder=2)
        ax.add_patch(nucleus)
        text_elem = ax.text(0, 0, "DNA\nreplicating", ha='center', va='center', fontsize=10, zorder=3)
        text_elements.append(text_elem)
    
    # Prophase
    elif stage_idx == 1:
        progress = min(time / 1.0, 1.0)  # Normalize to 0-1
        
        # Cell membrane
        cell_membrane = Circle((0, 0), cell_radius, fill=False, edgecolor='black', lw=3, zorder=1)
        ax.add_patch(cell_membrane)
        
        # Nucleus shrinking/disappearing
        nucleus_size = nucleus_radius * (1 - progress * 0.8)
        if nucleus_size > 0.1:
            nucleus = Circle((0, 0), nucleus_size, fill=True, facecolor='lightblue', 
                            edgecolor='darkblue', lw=2, alpha=0.5 * (1 - progress), zorder=2)
            ax.add_patch(nucleus)
        
        # Chromosomes condensing (appearing and condensing)
        num_visible = int(progress * num_chromosomes * 2)
        angle_step = 2 * np.pi / (num_chromosomes * 2)
        
        for i in range(num_visible):
            angle = i * angle_step
            dist = 0.3 + progress * 0.2
            center = [dist * np.cos(angle), dist * np.sin(angle)]
            chrom_angle = angle + np.pi/2
            color = colors[i // 2 % len(colors)]
            chrom = Chromosome(center, chrom_angle, length=0.1 + progress*0.05, 
                             width=0.05, color=color, pair_id=i//2)
            chrom.draw(ax)
            chromosomes.append(chrom)
        
        # Centrosomes appearing
        centrosome_dist = 0.4 * progress
        c1 = Circle((centrosome_dist, 0), 0.08, fill=True, facecolor='red', 
                   edgecolor='darkred', lw=2, zorder=4)
        c2 = Circle((-centrosome_dist, 0), 0.08, fill=True, facecolor='red', 
                   edgecolor='darkred', lw=2, zorder=4)
        ax.add_patch(c1)
        ax.add_patch(c2)
        centrosomes = [c1, c2]
    
    # Metaphase
    elif stage_idx == 2:
        # Cell membrane
        cell_membrane = Circle((0, 0), cell_radius, fill=False, edgecolor='black', lw=3, zorder=1)
        ax.add_patch(cell_membrane)
        
        # Chromosomes aligned at equator (pairs together, not separated yet)
        for pair_id in range(num_chromosomes):
            x_pos = -0.5 + (pair_id / max(1, num_chromosomes - 1)) * 1.0
            center = [x_pos, 0]
            chrom = Chromosome(center, np.pi/2, length=0.15, width=0.08, 
                             color=colors[pair_id % len(colors)], pair_id=pair_id)
            chrom.is_separated = False  # Ensure not separated in metaphase
            chrom.draw(ax)
            chromosomes.append(chrom)
        
        # Centrosomes at poles
        c1 = Circle((0, cell_radius * 0.7), 0.1, fill=True, facecolor='red', 
                   edgecolor='darkred', lw=2, zorder=4)
        c2 = Circle((0, -cell_radius * 0.7), 0.1, fill=True, facecolor='red', 
                   edgecolor='darkred', lw=2, zorder=4)
        ax.add_patch(c1)
        ax.add_patch(c2)
        centrosomes = [c1, c2]
        
        # Spindle fibers
        for chrom in chromosomes:
            cx, cy = chrom.center
            # Fiber to top centrosome
            ax.plot([cx, 0], [cy, cell_radius * 0.7], 'gray', lw=1, alpha=0.5, zorder=3)
            # Fiber to bottom centrosome
            ax.plot([cx, 0], [cy, -cell_radius * 0.7], 'gray', lw=1, alpha=0.5, zorder=3)
    
    # Anaphase
    elif stage_idx == 3:
        progress = min(time / 1.0, 1.0)
        
        # Cell membrane elongating
        elongation = progress * 0.4
        cell_membrane = Circle((0, 0), cell_radius + elongation, fill=False, 
                              edgecolor='black', lw=3, zorder=1)
        ax.add_patch(cell_membrane)
        
        # Chromosomes separating and moving to poles
        pole_top_y = cell_radius * 0.7
        pole_bottom_y = -cell_radius * 0.7
        
        # Each chromosome pair separates - one chromatid goes to each pole
        for pair_id in range(num_chromosomes):
            # Starting position (from metaphase plate)
            start_x = -0.5 + (pair_id / max(1, num_chromosomes - 1)) * 1.0
            start_y = 0
            
            # Separation distance increases with progress
            separation_x = progress * 0.2  # Horizontal spread
            
            # Top chromatid (moves to top pole)
            top_y = start_y + progress * pole_top_y
            top_x = start_x + separation_x * (1 if pair_id % 2 == 0 else -1)
            chrom_top = Chromosome([top_x, top_y], np.pi/2, length=0.15, width=0.08, 
                                 color=colors[pair_id % len(colors)], pair_id=pair_id)
            chrom_top.is_separated = progress > 0.2  # Separate earlier
            chrom_top.draw(ax)
            chromosomes.append(chrom_top)
            
            # Bottom chromatid (moves to bottom pole)
            bottom_y = start_y + progress * pole_bottom_y
            bottom_x = start_x - separation_x * (1 if pair_id % 2 == 0 else -1)
            chrom_bottom = Chromosome([bottom_x, bottom_y], np.pi/2, length=0.15, width=0.08, 
                                    color=colors[pair_id % len(colors)], pair_id=pair_id)
            chrom_bottom.is_separated = progress > 0.2  # Separate earlier
            chrom_bottom.draw(ax)
            chromosomes.append(chrom_bottom)
        
        # Centrosomes
        pole_top_pos = (0, pole_top_y)
        pole_bottom_pos = (0, pole_bottom_y)
        c1 = Circle(pole_top_pos, 0.1, fill=True, facecolor='red', 
                   edgecolor='darkred', lw=2, zorder=4)
        c2 = Circle(pole_bottom_pos, 0.1, fill=True, facecolor='red', 
                   edgecolor='darkred', lw=2, zorder=4)
        ax.add_patch(c1)
        ax.add_patch(c2)
        centrosomes = [c1, c2]
    
    # Telophase
    elif stage_idx == 4:
        progress = min(time / 1.0, 1.0)
        
        # Cell membrane pinching
        pinch = progress * 0.4
        # Draw two overlapping circles for pinching effect
        cell_membrane1 = Circle((0, pinch), cell_radius * 0.9, fill=False, 
                               edgecolor='black', lw=3, zorder=1)
        cell_membrane2 = Circle((0, -pinch), cell_radius * 0.9, fill=False, 
                               edgecolor='black', lw=3, zorder=1)
        ax.add_patch(cell_membrane1)
        ax.add_patch(cell_membrane2)
        cell_membrane = [cell_membrane1, cell_membrane2]
        
        # Chromosomes at poles, decondensing (fading out)
        pole_top = [0, cell_radius * 0.6]
        pole_bottom = [0, -cell_radius * 0.6]
        
        # Chromosomes become less visible as they decondense
        fade_progress = 1.0 - progress  # Fade out as telophase progresses
        
        if fade_progress > 0.1:  # Only show if still visible
            for i in range(num_chromosomes * 2):
                if i % 2 == 0:
                    center = pole_top
                else:
                    center = pole_bottom
                
                # Decondensing (getting smaller and fading)
                length = 0.15 * fade_progress
                width = 0.08 * fade_progress
                chrom = Chromosome(center, np.pi/2, length=length, width=width, 
                                 color=colors[i // 2 % len(colors)], pair_id=i//2)
                chrom.is_separated = True
                chrom.draw(ax)
                chromosomes.append(chrom)
        
        # Nuclei reforming (growing)
        nucleus_size = progress * nucleus_radius * 0.7
        if nucleus_size > 0.1:
            n1 = Circle(tuple(pole_top), nucleus_size, fill=True, facecolor='lightblue', 
                       edgecolor='darkblue', lw=2, alpha=0.5 + progress * 0.3, zorder=2)
            n2 = Circle(tuple(pole_bottom), nucleus_size, fill=True, facecolor='lightblue', 
                       edgecolor='darkblue', lw=2, alpha=0.5 + progress * 0.3, zorder=2)
            ax.add_patch(n1)
            ax.add_patch(n2)
            nucleus = [n1, n2]
    
    # Cytokinesis
    elif stage_idx == 5:
        progress = min(time / 1.0, 1.0)
        
        # Two separate cells (completely separated)
        # Increase separation significantly - start at 0.8 and go to 1.5
        separation = 0.8 + progress * 0.7  # Much more separation
        cell1 = Circle((0, separation), cell_radius * 0.85, fill=False, 
                      edgecolor='black', lw=3, zorder=1)
        cell2 = Circle((0, -separation), cell_radius * 0.85, fill=False, 
                      edgecolor='black', lw=3, zorder=1)
        ax.add_patch(cell1)
        ax.add_patch(cell2)
        cell_membrane = [cell1, cell2]
        
        # Nuclei in each cell (fully formed)
        nucleus_size = nucleus_radius * 0.7
        n1 = Circle((0, separation), nucleus_size, fill=True, facecolor='lightblue', 
                   edgecolor='darkblue', lw=2, alpha=0.6, zorder=2)
        n2 = Circle((0, -separation), nucleus_size, fill=True, facecolor='lightblue', 
                   edgecolor='darkblue', lw=2, alpha=0.6, zorder=2)
        ax.add_patch(n1)
        ax.add_patch(n2)
        nucleus = [n1, n2]
        
        # Chromosomes are completely decondensed (not visible in Cytokinesis)
        # Only show labels
        text1 = ax.text(0, separation, "Daughter\nCell 1", ha='center', va='center', 
               fontsize=11, fontweight='bold', zorder=4,
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        text2 = ax.text(0, -separation, "Daughter\nCell 2", ha='center', va='center', 
               fontsize=11, fontweight='bold', zorder=4,
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        text_elements.extend([text1, text2])
        
        # No chromosomes, no spindle fibers - just two separate cells
    
    # Update stage label
    stage_label.set_text(f"Stage: {stage_name}")
    
    # Update info text
    description = STAGE_DESCRIPTIONS.get(stage_name, "Unknown stage")
    # Wrap description if too long (manual wrapping)
    max_desc_len = 32
    if len(description) > max_desc_len:
        words = description.split()
        wrapped_desc = []
        current_line = ""
        for word in words:
            if len(current_line + word + " ") <= max_desc_len:
                current_line += word + " "
            else:
                if current_line:
                    wrapped_desc.append(current_line.strip())
                current_line = word + " "
        if current_line:
            wrapped_desc.append(current_line.strip())
        description = "\n".join(wrapped_desc)
    
    info_text.set_text(
        f"MITOSIS SIMULATOR\n"
        f"{'='*28}\n\n"
        f"Current Stage: {stage_name}\n"
        f"Stage {stage_idx + 1} of {len(STAGES)}\n\n"
        f"Description:\n{description}\n\n"
        f"Key Features:\n"
    )
    
    if stage_idx == 0:
        info_text.set_text(info_text.get_text() + 
            "• Cell growth\n"
            "• DNA replication\n"
            "• Preparation for division")
    elif stage_idx == 1:
        info_text.set_text(info_text.get_text() + 
            "• Chromosomes condense\n"
            "• Nuclear envelope breaks\n"
            "• Spindle apparatus forms")
    elif stage_idx == 2:
        info_text.set_text(info_text.get_text() + 
            "• Chromosomes align\n"
            "• At metaphase plate\n"
            "• Spindle fibers attach")
    elif stage_idx == 3:
        info_text.set_text(info_text.get_text() + 
            "• Sister chromatids separate\n"
            "• Move to opposite poles\n"
            "• Cell begins to elongate")
    elif stage_idx == 4:
        info_text.set_text(info_text.get_text() + 
            "• Chromosomes decondense\n"
            "• Nuclear envelopes reform\n"
            "• Cell membrane pinches")
    elif stage_idx == 5:
        info_text.set_text(info_text.get_text() + 
            "• Two daughter cells form\n"
            "• Each with full chromosome set\n"
            "• Process complete!")

# -----------------------------
# Controls
# -----------------------------
# Stage selector (radio buttons)
ax_stage = plt.axes([0.10, 0.10, 0.55, 0.12])
stage_radio = RadioButtons(ax_stage, list(STAGES.keys()), active=0)

# Buttons
ax_prev = plt.axes([0.10, 0.05, 0.12, 0.04])
btn_prev = Button(ax_prev, "◄ Previous")

ax_next = plt.axes([0.24, 0.05, 0.12, 0.04])
btn_next = Button(ax_next, "Next ►")

ax_animate = plt.axes([0.38, 0.05, 0.12, 0.04])
btn_animate = Button(ax_animate, "Animate")

ax_reset = plt.axes([0.52, 0.05, 0.12, 0.04])
btn_reset = Button(ax_reset, "Reset")

# Speed slider
ax_speed = plt.axes([0.70, 0.10, 0.12, 0.03])
speed_slider = Slider(ax_speed, "Speed", 0.5, 3.0, valinit=1.0, valstep=0.1)

# -----------------------------
# Event handlers
# -----------------------------
def on_stage_select(label):
    """Handle stage selection."""
    state["stage"] = STAGES[label]
    state["time"] = 0.0
    update_visualization()
    fig.canvas.draw_idle()

def on_prev(_):
    """Go to previous stage."""
    if state["stage"] > 0:
        state["stage"] -= 1
        state["time"] = 0.0
        stage_radio.set_active(state["stage"])
        update_visualization()
        fig.canvas.draw_idle()

def on_next(_):
    """Go to next stage."""
    if state["stage"] < len(STAGES) - 1:
        state["stage"] += 1
        state["time"] = 0.0
        stage_radio.set_active(state["stage"])
        update_visualization()
        fig.canvas.draw_idle()

def on_animate(_):
    """Toggle animation."""
    state["animate"] = not state["animate"]
    if state["animate"]:
        btn_animate.label.set_text("Stop")
    else:
        btn_animate.label.set_text("Animate")

def on_reset(_):
    """Reset to beginning."""
    # Stop animation first
    state["animate"] = False
    btn_animate.label.set_text("Animate")
    
    # Reset state to beginning
    state["stage"] = 0
    state["time"] = 0.0
    state["speed"] = 1.0  # Reset speed to default
    
    # Reset speed slider
    speed_slider.reset()
    
    # Update radio button
    stage_radio.set_active(0)
    
    # Clear all elements completely
    clear_elements()
    
    # Reset chromosome states by clearing the list
    global chromosomes
    chromosomes = []
    
    # Redraw visualization from scratch
    update_visualization()
    
    # Force redraw
    fig.canvas.draw_idle()
    fig.canvas.flush_events()

def on_speed_change(val):
    """Handle speed change."""
    state["speed"] = float(val)

stage_radio.on_clicked(on_stage_select)
btn_prev.on_clicked(on_prev)
btn_next.on_clicked(on_next)
btn_animate.on_clicked(on_animate)
btn_reset.on_clicked(on_reset)
speed_slider.on_changed(on_speed_change)

# -----------------------------
# Animation
# -----------------------------
def animate(_frame):
    """Animation function."""
    if state["animate"]:
        state["time"] += 0.02 * state["speed"]
        
        # Auto-advance to next stage when current stage completes
        if state["time"] > 1.0:
            state["time"] = 0.0
            if state["stage"] < len(STAGES) - 1:
                state["stage"] += 1
                stage_radio.set_active(state["stage"])
            else:
                state["animate"] = False
                btn_animate.label.set_text("Animate")
        
        update_visualization()
    
    return []

ani = FuncAnimation(fig, animate, interval=50, blit=False, cache_frame_data=False)

# Initial render
update_visualization()
plt.show()

