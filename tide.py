import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons, Button
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Polygon
from matplotlib import cm

# -----------------------------
# Simple equilibrium tide model
# -----------------------------
# We model tide height around Earth as proportional to P2(cos ψ) = (3cos^2ψ - 1)/2
# The overall amplitude scales ~ 1 / d^3 (tidal effect scales with distance cubed).

def p2(cospsi):
    """Legendre polynomial P2 for equilibrium tide model."""
    return 0.5 * (3 * cospsi**2 - 1)

def tide_profile(theta, body_angle, amplitude):
    """
    Calculate tide height profile around Earth.
    
    Parameters:
    -----------
    theta : array
        Angles around Earth (radians), measured from +x axis
    body_angle : float
        Direction of Moon/Sun (radians) from +x axis
    amplitude : float
        Overall tide amplitude (arbitrary units)
        
    Returns:
    --------
    array : Tide height at each angle
    """
    # ψ = angle between point direction and body direction
    psi = theta - body_angle
    cospsi = np.cos(psi)
    return amplitude * p2(cospsi)

# -----------------------------
# Initial parameters
# -----------------------------
R = 1.0  # Base Earth radius (normalized)
theta = np.linspace(0, 2*np.pi, 200)  # Angles for plotting

# State
state = {
    "moon_dist": 3.0,
    "moon_angle": 0.0,
    "sun_angle": 180.0,
    "exaggeration": 0.18,
    "sun_on": False,
    "animate": False,
    "sun_dist_factor": 4.0,  # Relative Sun distance factor
    "sun_strength": 0.46     # Sun tide strength relative to Moon
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(13, 7))
plt.subplots_adjust(left=0.08, bottom=0.30, right=0.68, top=0.95)

# Main plot axes
ax = plt.subplot(1, 1, 1)
ax.set_title("Sea Tides: Moon Gravity Gradient (Equilibrium Tide Model)", fontsize=12, fontweight='bold')
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-2.0, 2.0)
ax.set_ylim(-1.5, 1.5)
ax.grid(True, alpha=0.3)
ax.set_xlabel("x (normalized units)")
ax.set_ylabel("y (normalized units)")

# Earth outline (base circle)
earth_circle = Circle((0, 0), R, fill=True, color='lightblue', alpha=0.3, zorder=1)
ax.add_patch(earth_circle)
earth_line, = ax.plot(R*np.cos(theta), R*np.sin(theta), 'b-', lw=2.5, label="Earth", zorder=2)

# Tide visualization - will use filled polygon with colormap
tide_polygons = []  # List to track all tide polygons
tide_line, = ax.plot([], [], 'k-', lw=2.5, label="Ocean surface", zorder=3)

# Moon and Sun markers
moon_dot, = ax.plot([], [], marker="o", markersize=12, color='gray', 
                    markeredgecolor='black', markeredgewidth=1.5, label="Moon", zorder=5)
sun_dot, = ax.plot([], [], marker="*", markersize=15, color='yellow', 
                   markeredgecolor='orange', markeredgewidth=1, label="Sun", zorder=5)

# Direction lines (force vectors)
moon_dir_line, = ax.plot([], [], linestyle="--", lw=1.5, color='gray', alpha=0.6, zorder=4)
sun_dir_line, = ax.plot([], [], linestyle="--", lw=1.5, color='orange', alpha=0.6, zorder=4)

# High/low tide markers
high_tide_markers = []
low_tide_markers = []

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
# Moon distance slider
ax_md = plt.axes([0.10, 0.24, 0.55, 0.03])
moon_dist = Slider(ax_md, "Moon distance", 1.5, 6.0, valinit=state["moon_dist"], valstep=0.1)

# Moon angle slider
ax_ma = plt.axes([0.10, 0.20, 0.55, 0.03])
moon_ang = Slider(ax_ma, "Moon angle (deg)", 0, 360, valinit=state["moon_angle"], valstep=1)

# Exaggeration slider
ax_ex = plt.axes([0.10, 0.16, 0.55, 0.03])
exag = Slider(ax_ex, "Exaggeration factor", 0.0, 0.5, valinit=state["exaggeration"], valstep=0.01)

# Sun controls
ax_checks = plt.axes([0.70, 0.20, 0.12, 0.08])
checks = CheckButtons(ax_checks, ["Include Sun", "Animate"], [state["sun_on"], state["animate"]])

ax_sa = plt.axes([0.10, 0.12, 0.55, 0.03])
sun_ang = Slider(ax_sa, "Sun angle (deg)", 0, 360, valinit=state["sun_angle"], valstep=1)

# Sun strength slider
ax_ss = plt.axes([0.10, 0.08, 0.55, 0.03])
sun_strength = Slider(ax_ss, "Sun tide strength", 0.1, 1.0, valinit=state["sun_strength"], valstep=0.01)

# Buttons
ax_reset = plt.axes([0.70, 0.10, 0.12, 0.04])
btn_reset = Button(ax_reset, "Reset")

# -----------------------------
# Update function
# -----------------------------
def clear_tide_markers():
    """Remove high/low tide markers."""
    global high_tide_markers, low_tide_markers
    for m in high_tide_markers:
        m.remove()
    for m in low_tide_markers:
        m.remove()
    high_tide_markers = []
    low_tide_markers = []

def update():
    """Update the visualization."""
    global tide_polygons, high_tide_markers, low_tide_markers
    
    # Read UI state
    d_m = float(moon_dist.val)
    a_m = np.deg2rad(float(moon_ang.val))
    exaggeration = float(exag.val)
    sun_on = checks.get_status()[0]
    a_s = np.deg2rad(float(sun_ang.val))
    sun_str = float(sun_strength.val)
    
    # Update state
    state["moon_dist"] = d_m
    state["moon_angle"] = float(moon_ang.val)
    state["sun_angle"] = float(sun_ang.val)
    state["exaggeration"] = exaggeration
    state["sun_on"] = sun_on
    state["sun_strength"] = sun_str

    # Tidal amplitude scale ~ 1/d^3 (normalized)
    A_m = (1.0 / d_m**3)

    # Moon tide profile
    h = tide_profile(theta, a_m, A_m)

    # Optional Sun tide
    if sun_on:
        A_s = sun_str * (1.0 / (state["sun_dist_factor"]**3))
        h += tide_profile(theta, a_s, A_s)

    # Center the tide profile so average radius stays ~R
    h = h - np.mean(h)

    # Build deformed ocean radius
    r_ocean = R + exaggeration * h

    x_o = r_ocean * np.cos(theta)
    y_o = r_ocean * np.sin(theta)
    tide_line.set_data(x_o, y_o)
    
    # Remove old tide polygons
    for poly in tide_polygons:
        poly.remove()
    tide_polygons = []
    
    # Create color-coded fill based on tide height
    # Normalize heights for colormap
    h_min, h_max = np.min(h), np.max(h)
    if h_max > h_min:
        h_normalized = (h - h_min) / (h_max - h_min)
    else:
        h_normalized = np.ones_like(h) * 0.5
    
    colormap = cm.get_cmap('RdYlBu_r')
    colors = colormap(h_normalized)  # Red for high, Blue for low
    
    # Create filled polygon segments with color gradient
    n_segments = len(theta)
    for i in range(n_segments - 1):
        # Create triangle from center to two adjacent points
        poly_points = np.array([
            [0, 0],
            [x_o[i], y_o[i]],
            [x_o[i+1], y_o[i+1]]
        ])
        poly = Polygon(poly_points, closed=True, 
                      facecolor=colors[i], edgecolor='none', alpha=0.7, zorder=1)
        ax.add_patch(poly)
        tide_polygons.append(poly)

    # Place Moon marker
    moon_r = 1.5
    moon_dot.set_data([moon_r*np.cos(a_m)], [moon_r*np.sin(a_m)])
    moon_dir_line.set_data([0, moon_r*np.cos(a_m)], [0, moon_r*np.sin(a_m)])

    # Place Sun marker
    if sun_on:
        sun_r = 1.7
        sun_dot.set_data([sun_r*np.cos(a_s)], [sun_r*np.sin(a_s)])
        sun_dir_line.set_data([0, sun_r*np.cos(a_s)], [0, sun_r*np.sin(a_s)])
    else:
        sun_dot.set_data([], [])
        sun_dir_line.set_data([], [])

    # Clear old markers
    clear_tide_markers()
    
    # Find and mark high/low tide locations
    idx_max = np.argmax(r_ocean)
    idx_min = np.argmin(r_ocean)
    
    # Mark high tides (two bulges)
    for idx in [idx_max, (idx_max + len(theta)//2) % len(theta)]:
        x_ht = r_ocean[idx] * np.cos(theta[idx])
        y_ht = r_ocean[idx] * np.sin(theta[idx])
        marker = ax.plot([x_ht], [y_ht], marker='^', markersize=10, 
                        color='red', markeredgecolor='darkred', markeredgewidth=1.5, zorder=6)[0]
        high_tide_markers.append(marker)
    
    # Mark low tides
    for idx in [idx_min, (idx_min + len(theta)//2) % len(theta)]:
        x_lt = r_ocean[idx] * np.cos(theta[idx])
        y_lt = r_ocean[idx] * np.sin(theta[idx])
        marker = ax.plot([x_lt], [y_lt], marker='v', markersize=10, 
                        color='blue', markeredgecolor='darkblue', markeredgewidth=1.5, zorder=6)[0]
        low_tide_markers.append(marker)

    # Calculate statistics
    max_tide = np.max(r_ocean) - R
    min_tide = np.min(r_ocean) - R
    tide_range = max_tide - min_tide
    
    ang_max = np.rad2deg(theta[idx_max]) % 360
    ang_min = np.rad2deg(theta[idx_min]) % 360

    # Spring vs neap tide detection
    note = ""
    tide_type = "Normal"
    if sun_on:
        sep = abs(np.rad2deg((a_s - a_m)) % 360)
        sep = min(sep, 360 - sep)
        if sep < 20:
            note = "SPRING TIDE: Moon & Sun aligned → Maximum tides"
            tide_type = "Spring"
        elif abs(sep - 90) < 20 or abs(sep - 270) < 20:
            note = "NEAP TIDE: Moon & Sun at 90° → Minimum tides"
            tide_type = "Neap"
        else:
            note = "Intermediate tide configuration"
    else:
        note = "Moon-only tide (no Sun contribution)"

    info_text.set_text(
        f"TIDE SIMULATION\n"
        f"{'='*30}\n\n"
        f"Moon distance: {d_m:.2f}\n"
        f"Tidal strength: {A_m:.4f} (~1/d³)\n"
        f"Exaggeration: {exaggeration:.2f}x\n\n"
        f"Tide Statistics:\n"
        f"  Max height: +{max_tide:.4f}\n"
        f"  Min height: {min_tide:.4f}\n"
        f"  Range: {tide_range:.4f}\n\n"
        f"High tide at: {ang_max:.0f}° & {(ang_max+180)%360:.0f}°\n"
        f"Low tide at: {ang_min:.0f}° & {(ang_min+180)%360:.0f}°\n\n"
        f"Tide Type: {tide_type}\n"
        f"{note}\n\n"
        f"Color coding:\n"
        f"  Red = High tide\n"
        f"  Blue = Low tide"
    )

    fig.canvas.draw_idle()

def on_change(_):
    """Handle slider changes."""
    update()

moon_dist.on_changed(on_change)
moon_ang.on_changed(on_change)
exag.on_changed(on_change)
sun_ang.on_changed(on_change)
sun_strength.on_changed(on_change)

def on_check(label):
    """Handle checkbox changes."""
    if label == "Include Sun":
        state["sun_on"] = checks.get_status()[0]
    elif label == "Animate":
        state["animate"] = checks.get_status()[1]
    update()

checks.on_clicked(on_check)

def on_reset(_):
    """Reset all controls to defaults."""
    moon_dist.reset()
    moon_ang.reset()
    exag.reset()
    sun_ang.reset()
    sun_strength.reset()
    if checks.get_status()[0]:
        checks.set_active(0)
    if checks.get_status()[1]:
        checks.set_active(1)
    state["animate"] = False
    update()

btn_reset.on_clicked(on_reset)

# -----------------------------
# Animation
# -----------------------------
def animate(_frame):
    """Animation function for automatic Moon/Sun movement."""
    if not state["animate"]:
        return moon_dot, sun_dot, moon_dir_line, sun_dir_line, tide_line
    
    # Animate Moon (slow orbit)
    current_moon_angle = state["moon_angle"] + 0.5  # degrees per frame
    state["moon_angle"] = current_moon_angle % 360
    moon_ang.set_val(state["moon_angle"])
    
    # Animate Sun if enabled (much slower)
    if state["sun_on"]:
        current_sun_angle = state["sun_angle"] + 0.1  # degrees per frame
        state["sun_angle"] = current_sun_angle % 360
        sun_ang.set_val(state["sun_angle"])
    
    return moon_dot, sun_dot, moon_dir_line, sun_dir_line, tide_line

ani = FuncAnimation(fig, animate, interval=50, blit=False)

# Initial render
update()
plt.show()
