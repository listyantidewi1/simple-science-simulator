import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons, Button
from matplotlib.patches import Arc

# -----------------------------
# Helpers
# -----------------------------
def deg2rad(d): 
    return np.deg2rad(d)

def rad2deg(r): 
    return np.rad2deg(r)

def snell(n1, n2, theta1_rad):
    """
    Calculate refraction using Snell's law: n1 sin(θ1) = n2 sin(θ2)
    
    Returns:
    --------
    (has_refraction, theta2_rad, is_TIR, theta_critical_rad_or_None)
    """
    # Snell: n1 sin(theta1) = n2 sin(theta2)
    s1 = np.sin(theta1_rad)
    s2 = (n1 / n2) * s1

    theta_c = None
    is_TIR = False

    # Critical angle exists only if n1 > n2 (light going from denser to rarer medium)
    if n1 > n2:
        theta_c = np.arcsin(np.clip(n2 / n1, 0, 1))
        if np.abs(theta1_rad) > theta_c + 1e-12:
            is_TIR = True

    # Refraction possible if |sin(theta2)| <= 1
    if np.abs(s2) <= 1.0 and (not is_TIR):
        theta2 = np.arcsin(np.clip(s2, -1, 1))
        return True, theta2, False, theta_c

    return False, None, is_TIR, theta_c


def ray_segment(theta_rad, length=1.2, origin=(0, 0), direction="down"):
    """
    Calculate ray segment coordinates.
    
    Parameters:
    -----------
    theta_rad : float
        Angle from normal (vertical) in radians
    length : float
        Ray length
    origin : tuple
        Starting point (x, y)
    direction : str
        "down" for ray going into y<0, "up" for y>0
        
    Returns:
    --------
    ((x1, x2), (y1, y2)) : Ray coordinates
    """
    ox, oy = origin
    # Angle from normal: normal is vertical; convert to direction vector
    dx = np.sin(theta_rad)
    dy = np.cos(theta_rad)

    if direction == "down":
        dy = -abs(dy)
    else:
        dy = abs(dy)

    x2 = ox + length * dx
    y2 = oy + length * dy
    return (ox, x2), (oy, y2)


# -----------------------------
# Initial parameters
# -----------------------------
n1_init = 1.00  # air
n2_init = 1.33  # water
theta1_init_deg = 35.0

# Material presets
MATERIALS = {
    "Air": 1.00,
    "Water": 1.33,
    "Glass": 1.50,
    "Diamond": 2.42,
    "Crown Glass": 1.52,
    "Flint Glass": 1.62
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(13, 7))
plt.subplots_adjust(left=0.08, bottom=0.30, right=0.68, top=0.95)

# Main plot axes
ax = plt.subplot(1, 1, 1)
ax.set_title("Snell's Law: Refraction & Total Internal Reflection", fontsize=12, fontweight='bold')
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.grid(True, alpha=0.3)

# Interface boundary at y=0
ax.axhline(0, lw=3, color='black', zorder=2)

# Shade the media with better colors
ax.fill_between([-2, 2], 0, 2, alpha=0.15, color='lightblue', zorder=0)   # medium 1
ax.fill_between([-2, 2], -2, 0, alpha=0.20, color='lightcyan', zorder=0)  # medium 2
ax.text(-1.4, 1.2, "Medium 1 (n₁)", fontsize=11, fontweight='bold', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
ax.text(-1.4, -1.3, "Medium 2 (n₂)", fontsize=11, fontweight='bold',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

# Normal line
normal_line, = ax.plot([0, 0], [-1.5, 1.5], linestyle="--", lw=1.5, color='gray', alpha=0.7, zorder=1)

# Rays with colors
inc_line, = ax.plot([], [], lw=3, color='blue', label="Incident ray", zorder=3)
refr_line, = ax.plot([], [], lw=3, color='green', label="Refracted ray", zorder=3)
refl_line, = ax.plot([], [], lw=2.5, linestyle=":", color='orange', label="Reflected ray", zorder=3)

# Critical angle marker
crit_line, = ax.plot([], [], lw=2, linestyle="--", color='red', alpha=0.6, label="Critical angle", zorder=3)

# Angle arcs (will be created dynamically)
angle_arcs = []

ax.legend(loc="upper left", fontsize=9)

# Info text panel - positioned on the right side
ax_text = plt.axes([0.70, 0.30, 0.29, 0.65])
ax_text.axis('off')
info_text = ax_text.text(
    0.05, 0.98, "",
    transform=ax_text.transAxes,
    va="top",
    ha="left",
    fontsize=9,
    family='monospace',
    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.95, edgecolor="gray")
)

# -----------------------------
# Controls
# -----------------------------
# Incident angle slider (full range)
ax_theta = plt.axes([0.10, 0.24, 0.55, 0.03])
theta_slider = Slider(ax_theta, "Incident angle θ₁ (deg)", -89, 89, valinit=theta1_init_deg, valstep=1)

# Refractive indices
ax_n1 = plt.axes([0.10, 0.20, 0.55, 0.03])
n1_slider = Slider(ax_n1, "n₁ (Medium 1)", 1.00, 2.50, valinit=n1_init, valstep=0.01)

ax_n2 = plt.axes([0.10, 0.16, 0.55, 0.03])
n2_slider = Slider(ax_n2, "n₂ (Medium 2)", 1.00, 2.50, valinit=n2_init, valstep=0.01)

# Checkboxes
ax_checks = plt.axes([0.70, 0.20, 0.12, 0.08])
checks = CheckButtons(ax_checks, ["Show angles", "Show critical"], [True, True])

# Buttons
ax_reset = plt.axes([0.70, 0.12, 0.12, 0.04])
btn_reset = Button(ax_reset, "Reset")

# Preset buttons
ax_air_water = plt.axes([0.70, 0.16, 0.12, 0.03])
btn_air_water = Button(ax_air_water, "Air→Water")

ax_glass_air = plt.axes([0.84, 0.16, 0.12, 0.03])
btn_glass_air = Button(ax_glass_air, "Glass→Air")

# -----------------------------
# Update function
# -----------------------------
def clear_angle_arcs():
    """Remove angle arc annotations."""
    global angle_arcs
    for arc in angle_arcs:
        arc.remove()
    angle_arcs = []

def draw_angle_arc(ax, center, radius, start_angle, end_angle, color='black', label=''):
    """Draw an angle arc with label."""
    arc = Arc(center, radius*2, radius*2, angle=0, 
              theta1=rad2deg(start_angle), theta2=rad2deg(end_angle),
              color=color, lw=1.5, zorder=4)
    ax.add_patch(arc)
    angle_arcs.append(arc)
    
    # Add label
    mid_angle = (start_angle + end_angle) / 2
    label_x = center[0] + radius * 0.7 * np.sin(mid_angle)
    label_y = center[1] + radius * 0.7 * np.cos(mid_angle)
    ax.text(label_x, label_y, label, fontsize=8, color=color, 
            ha='center', va='center', zorder=5,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

def update_plot():
    """Update the visualization."""
    global angle_arcs
    
    n1 = float(n1_slider.val)
    n2 = float(n2_slider.val)
    theta1_deg = float(theta_slider.val)
    theta1 = deg2rad(theta1_deg)
    
    show_angles = checks.get_status()[0]
    show_crit = checks.get_status()[1]

    # Clear old angle arcs
    clear_angle_arcs()

    # Incident ray: comes from medium 1 (above), heading down to boundary
    (x0, x1), (y0, y1) = ray_segment(theta1, length=1.3, origin=(0, 0), direction="up")
    inc_line.set_data([x1, 0], [y1, 0])

    # Reflected ray (always possible): symmetric angle in medium 1
    (rx0, rx1), (ry0, ry1) = ray_segment(theta1, length=1.0, origin=(0, 0), direction="up")
    refl_line.set_data([0, rx1], [0, ry1])

    has_ref, theta2, is_tir, theta_c = snell(n1, n2, theta1)

    # Refracted ray (only if not TIR)
    if has_ref:
        (tx0, tx1), (ty0, ty1) = ray_segment(theta2, length=1.3, origin=(0, 0), direction="down")
        refr_line.set_data([0, tx1], [0, ty1])
    else:
        refr_line.set_data([], [])

    # Critical angle line (only if n1 > n2 and toggle on)
    if show_crit and (theta_c is not None):
        (cx0, cx1), (cy0, cy1) = ray_segment(theta_c, length=1.0, origin=(0, 0), direction="up")
        crit_line.set_data([0, cx1], [0, cy1])
    else:
        crit_line.set_data([], [])

    # Draw angle arcs if enabled
    if show_angles:
        arc_radius = 0.25
        # Incident angle arc (from normal to incident ray)
        if theta1 > 0:
            draw_angle_arc(ax, (0, 0), arc_radius, 0, theta1, 'blue', f'θ₁={theta1_deg:.1f}°')
        else:
            draw_angle_arc(ax, (0, 0), arc_radius, theta1, 0, 'blue', f'θ₁={theta1_deg:.1f}°')
        
        # Refracted angle arc (if refraction exists)
        if has_ref and theta2 is not None:
            draw_angle_arc(ax, (0, 0), arc_radius, 0, -theta2, 'green', f'θ₂={rad2deg(theta2):.1f}°')
        
        # Reflected angle arc
        draw_angle_arc(ax, (0, 0), arc_radius, 0, -theta1, 'orange', 'θᵣ')

    # Calculate Snell's law verification
    if has_ref and theta2 is not None:
        lhs = n1 * np.sin(theta1)
        rhs = n2 * np.sin(theta2)
        snell_check = f"Snell's law: {n1:.2f}×sin({theta1_deg:.1f}°) = {n2:.2f}×sin({rad2deg(theta2):.1f}°)\n"
        snell_check += f"  → {lhs:.4f} = {rhs:.4f} ✓"
    else:
        snell_check = "Snell's law: Cannot calculate (TIR or no refraction)"

    # Text info
    if theta_c is None:
        crit_str = "Critical angle: N/A (n₁ ≤ n₂)"
        tir_note = ""
    else:
        crit_str = f"Critical angle θc: {rad2deg(theta_c):.1f}°"
        if is_tir:
            tir_note = f"\n⚠ TOTAL INTERNAL REFLECTION (θ₁ > θc)"
        else:
            tir_note = f"\n(θ₁ < θc, refraction possible)"

    if is_tir:
        refr_str = "Refraction: NONE"
        theta2_str = "θ₂: N/A (TIR)"
        status = "🔴 TOTAL INTERNAL REFLECTION"
    else:
        if has_ref:
            theta2_str = f"θ₂: {rad2deg(theta2):.1f}°"
            refr_str = "Refraction: YES"
            if n1 > n2:
                status = "🟢 Bends away from normal"
            else:
                status = "🟢 Bends toward normal"
        else:
            theta2_str = "θ₂: N/A"
            refr_str = "Refraction: NONE"
            status = "⚪ No refraction"

    # Determine which medium is denser
    if n1 > n2:
        density_note = f"Medium 1 is DENSER (n₁={n1:.2f} > n₂={n2:.2f})"
    elif n2 > n1:
        density_note = f"Medium 2 is DENSER (n₂={n2:.2f} > n₁={n1:.2f})"
    else:
        density_note = "Media have EQUAL refractive indices"

    info_text.set_text(
        f"SNELL'S LAW SIMULATOR\n"
        f"{'='*30}\n\n"
        f"Refractive Indices:\n"
        f"  n₁ = {n1:.2f}\n"
        f"  n₂ = {n2:.2f}\n"
        f"  {density_note}\n\n"
        f"Angles:\n"
        f"  {theta2_str}\n"
        f"  {refr_str}\n\n"
        f"{snell_check}\n\n"
        f"{crit_str}{tir_note}\n\n"
        f"Status: {status}\n\n"
        f"Note: Angles measured from\n"
        f"the NORMAL (dashed line)"
    )

    fig.canvas.draw_idle()


def on_slider(_):
    """Handle slider changes."""
    update_plot()

theta_slider.on_changed(on_slider)
n1_slider.on_changed(on_slider)
n2_slider.on_changed(on_slider)

def on_check(label):
    """Handle checkbox changes."""
    update_plot()

checks.on_clicked(on_check)

def on_reset(_):
    """Reset all controls to defaults."""
    theta_slider.reset()
    n1_slider.reset()
    n2_slider.reset()
    if not checks.get_status()[0]:
        checks.set_active(0)
    if not checks.get_status()[1]:
        checks.set_active(1)
    update_plot()

def on_air_water(_):
    """Set Air→Water preset."""
    n1_slider.set_val(MATERIALS["Air"])
    n2_slider.set_val(MATERIALS["Water"])
    update_plot()

def on_glass_air(_):
    """Set Glass→Air preset (for TIR demonstration)."""
    n1_slider.set_val(MATERIALS["Glass"])
    n2_slider.set_val(MATERIALS["Air"])
    theta_slider.set_val(45.0)  # Good angle to show TIR
    update_plot()

btn_reset.on_clicked(on_reset)
btn_air_water.on_clicked(on_air_water)
btn_glass_air.on_clicked(on_glass_air)

# Initial render
update_plot()
plt.show()
