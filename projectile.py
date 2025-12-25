import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons

# ----------------------------
# Physics engine (Euler integration)
# ----------------------------
def simulate(v0, theta, g, drag_on, k, dt=0.01, tmax=15.0):
    """
    Simple 2D projectile simulation from origin with optional air drag.
    Drag model: a = -k * v * |v|  (quadratic-ish), applied to both components.
    Uses explicit Euler integration (good for classroom exploration).
    """
    x, y = 0.0, 0.0
    vx = v0 * np.cos(theta)
    vy = v0 * np.sin(theta)

    xs, ys = [x], [y]
    for _ in range(int(tmax / dt)):
        v = np.hypot(vx, vy)

        ax = 0.0
        ay = -g

        if drag_on and v > 1e-9:
            ax += -k * vx * v
            ay += -k * vy * v

        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt

        if y < 0:
            y = 0
            xs.append(x)
            ys.append(y)
            break

        xs.append(x)
        ys.append(y)

    return np.array(xs), np.array(ys)

# ----------------------------
# Game / UI state
# ----------------------------
rng = np.random.default_rng(42)

LAUNCH_POINT = np.array([0.0, 0.0])

state = {
    "g": 9.81,
    "drag_on": False,
    "k": 0.02,          # drag strength (tweakable)
    "last_v0": 20.0,
    "last_theta": np.deg2rad(45),
    "score": 0,
    "attempts": 0
}

def new_target():
    # Place target in a reasonable range for classroom play
    tx = float(rng.uniform(15, 60))
    ty = float(rng.uniform(2, 18))
    return np.array([tx, ty])

target = new_target()

# ----------------------------
# Plot setup
# ----------------------------
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(left=0.10, bottom=0.28, right=0.85)

ax.set_title("Interactive Projectile Motion: Click to Aim + Hit the Target")
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.grid(True)

# Plot elements
traj_line, = ax.plot([], [], lw=2, label="Trajectory")
launch_dot, = ax.plot([LAUNCH_POINT[0]], [LAUNCH_POINT[1]], marker="o", markersize=8, label="Launch")
target_dot, = ax.plot([target[0]], [target[1]], marker="X", markersize=12, linestyle="None", label="Target")
aim_line, = ax.plot([], [], lw=1, linestyle="--", label="Aim vector")

status_text = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top")

ax.legend(loc="upper right")

def autoscale():
    # Keep view big enough; expand based on target and last trajectory
    xmax = max(70, target[0] * 1.2)
    ymax = max(25, target[1] * 1.6)
    ax.set_xlim(-2, xmax)
    ax.set_ylim(0, ymax)

autoscale()

# ----------------------------
# Controls
# ----------------------------
# Gravity slider
ax_g = plt.axes([0.10, 0.16, 0.72, 0.03])
g_slider = Slider(ax_g, "Gravity g (m/s²)", 1.0, 20.0, valinit=state["g"], valstep=0.1)

# Drag checkbox
ax_drag = plt.axes([0.87, 0.55, 0.12, 0.12])
drag_check = CheckButtons(ax_drag, ["Air Drag"], [state["drag_on"]])

# Buttons
ax_reset = plt.axes([0.10, 0.06, 0.15, 0.06])
btn_reset = Button(ax_reset, "Reset")

ax_step = plt.axes([0.27, 0.06, 0.15, 0.06])
btn_replay = Button(ax_step, "Replay Shot")

ax_newt = plt.axes([0.44, 0.06, 0.20, 0.06])
btn_new_target = Button(ax_newt, "New Target")

ax_clear = plt.axes([0.66, 0.06, 0.16, 0.06])
btn_clear = Button(ax_clear, "Clear Trail")

# ----------------------------
# Helper functions
# ----------------------------
def update_status(extra=""):
    v0 = state["last_v0"]
    theta_deg = np.rad2deg(state["last_theta"])
    drag = "ON" if state["drag_on"] else "OFF"
    status_text.set_text(
        f"Score: {state['score']}  |  Attempts: {state['attempts']}\n"
        f"Last shot: v0={v0:.1f} m/s, angle={theta_deg:.0f}°  |  g={state['g']:.2f}, drag={drag}\n"
        f"Target: ({target[0]:.1f}, {target[1]:.1f})\n"
        f"{extra}\n"
        "How to play: Click in the plot to aim & set speed. Farther click = faster shot."
    )

def set_target(new_t):
    global target
    target = new_t
    target_dot.set_data([target[0]], [target[1]])
    autoscale()
    update_status("New target set. Try to hit it!")

def clear_trail():
    traj_line.set_data([], [])
    aim_line.set_data([], [])
    fig.canvas.draw_idle()

def evaluate_hit(xs, ys, hit_radius=1.5):
    # Minimum distance from any trajectory point to target
    dx = xs - target[0]
    dy = ys - target[1]
    dmin = float(np.min(np.hypot(dx, dy)))
    return dmin <= hit_radius, dmin

def shoot(v0, theta):
    state["last_v0"] = float(v0)
    state["last_theta"] = float(theta)

    xs, ys = simulate(
        v0=v0,
        theta=theta,
        g=state["g"],
        drag_on=state["drag_on"],
        k=state["k"]
    )

    traj_line.set_data(xs, ys)

    # Aim line for visualization (fixed length)
    L = 10
    axx = [LAUNCH_POINT[0], LAUNCH_POINT[0] + L * np.cos(theta)]
    ayy = [LAUNCH_POINT[1], LAUNCH_POINT[1] + L * np.sin(theta)]
    aim_line.set_data(axx, ayy)

    state["attempts"] += 1
    hit, dmin = evaluate_hit(xs, ys)

    if hit:
        state["score"] += 1
        update_status(f"HIT! Minimum distance to target: {dmin:.2f} m")
    else:
        update_status(f"Missed. Minimum distance to target: {dmin:.2f} m")

    fig.canvas.draw_idle()

# ----------------------------
# Event handlers
# ----------------------------
def on_click(event):
    # Only respond to clicks inside the axes
    if event.inaxes != ax:
        return

    # Vector from launch point to click point
    cx, cy = float(event.xdata), float(event.ydata)
    vec = np.array([cx, cy]) - LAUNCH_POINT

    # Avoid degenerate clicks
    if np.linalg.norm(vec) < 1e-6:
        return

    theta = np.arctan2(vec[1], vec[0])

    # Map click distance to speed (tunable scale)
    # Constrain to reasonable student-friendly values
    dist = float(np.linalg.norm(vec))
    v0 = np.clip(dist * 0.9, 3.0, 60.0)

    shoot(v0, theta)

def on_g_change(val):
    state["g"] = float(val)
    update_status("Gravity changed. Try the same aim and compare the outcome.")
    fig.canvas.draw_idle()

def on_drag_toggle(label):
    state["drag_on"] = not state["drag_on"]
    update_status("Air drag toggled. Compare range and peak height.")
    fig.canvas.draw_idle()

def on_reset(event):
    state["score"] = 0
    state["attempts"] = 0
    g_slider.set_val(9.81)
    # Keep target, clear trajectory
    clear_trail()
    update_status("Reset score/attempts. Click to launch.")
    fig.canvas.draw_idle()

def on_replay(event):
    clear_trail()
    shoot(state["last_v0"], state["last_theta"])

def on_new_target(event):
    clear_trail()
    set_target(new_target())

def on_clear(event):
    clear_trail()
    update_status("Cleared trail. Click to launch.")
    fig.canvas.draw_idle()

# ----------------------------
# Wire up UI
# ----------------------------
fig.canvas.mpl_connect("button_press_event", on_click)
g_slider.on_changed(on_g_change)
drag_check.on_clicked(on_drag_toggle)
btn_reset.on_clicked(on_reset)
btn_replay.on_clicked(on_replay)
btn_new_target.on_clicked(on_new_target)
btn_clear.on_clicked(on_clear)

update_status("Click to launch your first shot.")
plt.show()
