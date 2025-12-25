import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Polygon
from matplotlib import cm

# -----------------------------
# Kepler orbit utilities
# -----------------------------
def solve_kepler(M, e, tol=1e-10, max_iters=50):
    """
    Solve Kepler's equation: M = E - e sin(E) for E (eccentric anomaly)
    using Newton-Raphson with convergence checking.
    
    Parameters:
    -----------
    M : float or array
        Mean anomaly (radians)
    e : float
        Eccentricity (0 <= e < 1)
    tol : float
        Convergence tolerance
    max_iters : int
        Maximum iterations
        
    Returns:
    --------
    E : float or array
        Eccentric anomaly (radians)
    """
    # Handle array inputs
    M = np.asarray(M)
    scalar_input = M.ndim == 0
    if scalar_input:
        M = M[None]
    
    # Initial guess: better for high eccentricity
    E = np.where(e < 0.8, M, np.pi)
    
    for _ in range(max_iters):
        f = E - e * np.sin(E) - M
        fp = 1 - e * np.cos(E)
        
        # Avoid division by zero (shouldn't happen for e < 1, but be safe)
        delta = np.where(np.abs(fp) > 1e-12, f / fp, 0)
        E_new = E - delta
        
        # Check convergence
        if np.all(np.abs(delta) < tol):
            break
            
        E = E_new
    
    return E[0] if scalar_input else E

def orbit_point(a, e, M):
    """
    From mean anomaly M, compute position (x,y) and velocity for an orbit with 
    semi-major axis a and eccentricity e, with the Sun at one focus.
    
    Returns:
    --------
    x, y : float
        Position coordinates
    r : float
        Distance from focus
    f : float
        True anomaly (radians)
    vx, vy : float
        Velocity components (in units where GM=1, or scaled)
    """
    E = solve_kepler(M, e)
    
    # True anomaly
    cosf = (np.cos(E) - e) / (1 - e*np.cos(E))
    sinf = (np.sqrt(1 - e**2) * np.sin(E)) / (1 - e*np.cos(E))
    f = np.arctan2(sinf, cosf)

    # Distance from focus
    r = a * (1 - e**2) / (1 + e*np.cos(f))

    x = r * np.cos(f)
    y = r * np.sin(f)
    
    # Velocity components (using vis-viva equation and angular momentum conservation)
    # For unit GM: v^2 = GM(2/r - 1/a), and h = r^2 * df/dt = sqrt(GM*a*(1-e^2))
    # Angular velocity: df/dt = h / r^2
    h = np.sqrt(a * (1 - e**2))  # angular momentum (scaled, assuming GM=1)
    omega = h / (r * r)  # angular velocity
    
    # Velocity in polar coordinates: radial = dr/dt, tangential = r * df/dt
    # dr/dt = (a(1-e^2)e sin(f)) / (1+e cos(f))^2 * df/dt
    # For simplicity, compute velocity from orbital mechanics
    # v_r = sqrt(GM/(a(1-e^2))) * e*sin(f)
    # v_t = sqrt(GM/(a(1-e^2))) * (1 + e*cos(f))
    v_mag_sq = (2/r - 1/a)  # vis-viva (assuming GM=1)
    v_mag = np.sqrt(max(0, v_mag_sq))
    
    # Velocity direction: perpendicular to radius vector, with radial component
    # Using conservation of angular momentum and energy
    v_radial = np.sqrt(1/(a*(1-e**2))) * e * np.sin(f)
    v_tangential = np.sqrt(1/(a*(1-e**2))) * (1 + e*np.cos(f))
    
    # Convert to Cartesian
    vx = v_radial * np.cos(f) - v_tangential * np.sin(f)
    vy = v_radial * np.sin(f) + v_tangential * np.cos(f)
    
    return x, y, r, f, vx, vy

def triangle_area(x1, y1, x2, y2):
    # area of triangle with vertices (0,0), (x1,y1), (x2,y2)
    return 0.5 * abs(x1*y2 - y1*x2)

# -----------------------------
# Initial parameters
# -----------------------------
a = 1.0            # semi-major axis (scaled units)
e0 = 0.35          # eccentricity (0 circle, close to 1 very stretched)
dt0 = 0.08         # mean anomaly step per frame (acts like time step)
num_wedges = 8     # how many equal-time wedges to display

# State
state = {
    "e": e0,
    "dt": dt0,
    "M": 0.0,
    "paused": False,
    "history": []  # store recent points for wedge display
}

# -----------------------------
# Figure layout
# -----------------------------
fig = plt.figure(figsize=(12, 6))
plt.subplots_adjust(left=0.08, bottom=0.22, right=0.70, top=0.95)

# Main plot axes (animation area)
ax = plt.subplot(1, 1, 1)
ax.set_title("Kepler's 2nd Law: Equal Areas in Equal Times")
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-1.8, 1.2)
ax.set_ylim(-1.3, 1.3)
ax.grid(True)
ax.set_xlabel("x (AU, scaled)")
ax.set_ylabel("y (AU, scaled)")

# Sun at focus
sun, = ax.plot([0], [0], marker="o", markersize=10, label="Sun")

# Orbit curve (will update when e changes)
orbit_line, = ax.plot([], [], lw=2, label="Orbit")

# Planet point
planet, = ax.plot([], [], marker="o", markersize=8, label="Planet", color="blue")

# Radius line Sun->Planet
radius_line, = ax.plot([], [], lw=1.5, color="gray", alpha=0.5)

# Velocity vector
velocity_arrow = None  # Will be created dynamically

# Wedge patches (polygons)
wedge_polys = []

# Text panel - positioned on the right side, outside the plot area
ax_text = plt.axes([0.72, 0.22, 0.27, 0.73])
ax_text.axis('off')  # Hide axes
info_text = ax_text.text(
    0.05, 0.98, "",
    transform=ax_text.transAxes,
    va="top",
    ha="left",
    fontsize=9,
    family='monospace',  # Monospace for better alignment
    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.95, edgecolor="gray")
)

ax.legend(loc="lower left")

# -----------------------------
# Controls
# -----------------------------
ax_e = plt.axes([0.10, 0.12, 0.80, 0.03])
e_slider = Slider(ax_e, "Eccentricity (e)", 0.0, 0.85, valinit=e0, valstep=0.01)

ax_dt = plt.axes([0.10, 0.07, 0.80, 0.03])
dt_slider = Slider(ax_dt, "Time step (Δt)", 0.01, 0.20, valinit=dt0, valstep=0.01)

ax_btn = plt.axes([0.10, 0.015, 0.18, 0.04])
btn_play = Button(ax_btn, "Play / Pause")

ax_reset = plt.axes([0.30, 0.015, 0.18, 0.04])
btn_reset = Button(ax_reset, "Reset Orbit")

# -----------------------------
# Orbit drawing
# -----------------------------
def redraw_orbit():
    """Vectorized orbit drawing for better performance."""
    e = state["e"]
    Ms = np.linspace(0, 2*np.pi, 500)
    # Vectorize the computation
    Es = solve_kepler(Ms, e)
    cosf = (np.cos(Es) - e) / (1 - e*np.cos(Es))
    sinf = (np.sqrt(1 - e**2) * np.sin(Es)) / (1 - e*np.cos(Es))
    f = np.arctan2(sinf, cosf)
    r = a * (1 - e**2) / (1 + e*np.cos(f))
    xs = r * np.cos(f)
    ys = r * np.sin(f)
    orbit_line.set_data(xs, ys)

def clear_wedges():
    global wedge_polys
    for p in wedge_polys:
        p.remove()
    wedge_polys = []

def update_info(latest_area=None, areas=None, vx=None, vy=None, r=None):
    """Update information panel with orbital parameters and statistics."""
    e = state["e"]
    dt = state["dt"]
    
    # Orbital parameters
    perihelion = a * (1 - e)  # closest distance
    aphelion = a * (1 + e)    # farthest distance
    
    # Orbital period (assuming GM=1, period = 2π * sqrt(a^3))
    period = 2 * np.pi * np.sqrt(a**3)
    
    # Current speed
    if vx is not None and vy is not None:
        speed = np.hypot(vx, vy)
    else:
        speed = 0.0
    
    # Area statistics
    area_stats = ""
    if areas and len(areas) > 0:
        mean_area = np.mean(areas)
        std_area = np.std(areas)
        cv = (std_area / mean_area * 100) if mean_area > 0 else 0  # coefficient of variation
        area_stats = (
            f"\nArea statistics ({len(areas)} wedges):\n"
            f"  Mean: {mean_area:.6f}\n"
            f"  Std dev: {std_area:.6f}\n"
            f"  CV: {cv:.2f}% (lower = more equal)"
        )

    msg = (
        f"Eccentricity e = {e:.2f}\n"
        f"Time step Δt = {dt:.3f}\n"
        f"Orbital period T = {period:.2f} (scaled units)\n"
        f"Perihelion: {perihelion:.3f} AU\n"
        f"Aphelion: {aphelion:.3f} AU\n"
        f"Current speed: {speed:.3f}\n"
    )
    if r is not None:
        msg += f"Current distance: {r:.3f} AU\n"
    msg += "Kepler's 2nd Law: wedges should have similar area"
    if latest_area is not None:
        msg += f"\nLatest wedge area: {latest_area:.6f}"
    if area_stats:
        msg += area_stats
    info_text.set_text(msg)

# -----------------------------
# Wedge drawing
# -----------------------------
def draw_wedges():
    """
    Draw wedges for the most recent (num_wedges+1) points.
    Each wedge is triangle between consecutive points and the Sun.
    Uses color gradient to visualize area differences.
    """
    clear_wedges()
    pts = state["history"][-(num_wedges+1):]
    if len(pts) < 2:
        return

    areas = []
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        A = triangle_area(x1, y1, x2, y2)
        areas.append(A)

    # Color code wedges based on area (normalized)
    # Use a colormap to visualize area differences
    colors_list = []
    if len(areas) > 0:
        areas_arr = np.array(areas)
        mean_area = np.mean(areas_arr)
        if mean_area > 0:
            normalized = np.clip(areas_arr / (mean_area * 1.5), 0, 1)
            colormap = cm.get_cmap('viridis')
            colors_rgba = colormap(normalized)
            colors_list = [colors_rgba[i] for i in range(len(areas))]
        else:
            colors_list = ['blue'] * len(areas)
    else:
        colors_list = ['blue'] * max(len(pts) - 1, 1)
    
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        poly = Polygon(
            [[0, 0], [x1, y1], [x2, y2]], 
            closed=True, 
            alpha=0.3,
            facecolor=colors_list[i] if i < len(colors_list) else 'blue',
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(poly)
        wedge_polys.append(poly)

    # Update info with area statistics
    return areas

# -----------------------------
# UI callbacks
# -----------------------------
def on_e_change(val):
    """Handle eccentricity slider change."""
    global velocity_arrow
    state["e"] = float(val)
    state["M"] = 0.0
    state["history"] = []
    if velocity_arrow is not None:
        velocity_arrow.remove()
        velocity_arrow = None
    redraw_orbit()
    clear_wedges()
    update_info()
    fig.canvas.draw_idle()

def on_dt_change(val):
    state["dt"] = float(val)
    update_info()
    fig.canvas.draw_idle()

def on_play(_):
    state["paused"] = not state["paused"]

def on_reset(_):
    """Reset animation to initial state."""
    global velocity_arrow
    state["M"] = 0.0
    state["history"] = []
    if velocity_arrow is not None:
        velocity_arrow.remove()
        velocity_arrow = None
    clear_wedges()
    update_info()
    fig.canvas.draw_idle()

e_slider.on_changed(on_e_change)
dt_slider.on_changed(on_dt_change)
btn_play.on_clicked(on_play)
btn_reset.on_clicked(on_reset)

# Initial draw
redraw_orbit()
update_info()

# -----------------------------
# Animation
# -----------------------------
def animate(_frame):
    """Animation frame update."""
    global velocity_arrow
    
    if state["paused"]:
        return planet, radius_line, orbit_line, info_text

    e = state["e"]
    dt = state["dt"]

    # Advance "time" (mean anomaly)
    state["M"] = (state["M"] + dt) % (2*np.pi)

    x, y, r, f, vx, vy = orbit_point(a, e, state["M"])

    # Update planet position
    planet.set_data([x], [y])

    # Update radius line
    radius_line.set_data([0, x], [0, y])
    
    # Update velocity vector visualization
    if velocity_arrow is not None:
        velocity_arrow.remove()
    # Scale velocity arrow for visibility (arbitrary scale factor)
    v_scale = 0.3
    velocity_arrow = ax.arrow(
        x, y, vx * v_scale, vy * v_scale,
        head_width=0.05, head_length=0.05,
        fc='red', ec='red', alpha=0.7, zorder=5
    )

    # Save history for wedges
    state["history"].append((x, y))
    if len(state["history"]) > (num_wedges + 1):
        state["history"] = state["history"][-(num_wedges + 1):]

    # Draw wedges and get area statistics
    areas = draw_wedges()
    
    # Update info panel
    update_info(
        latest_area=areas[-1] if areas and len(areas) > 0 else None,
        areas=areas,
        vx=vx,
        vy=vy,
        r=r
    )
    
    return planet, radius_line, orbit_line, info_text

ani = FuncAnimation(fig, animate, interval=40, blit=False)
plt.show()
