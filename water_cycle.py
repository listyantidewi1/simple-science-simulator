import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle, Polygon, FancyArrowPatch, Ellipse
import matplotlib.patches as mpatches

# -----------------------------
# Water Cycle Simulator
# For Junior High School Earth Science
# -----------------------------

# State
state = {
    "temperature": 25,      # Temperature in Celsius (10-40)
    "humidity": 50,         # Humidity level (0-100)
    "wind_speed": 30,       # Wind speed (0-100)
    "sunlight": 70,         # Sunlight intensity (0-100)
    "is_animating": False,
    "animation_time": 0.0,
    "speed": 1.0
}

# Water particles for visualization
water_particles = []
cloud_particles = []
rain_drops = []
snow_flakes = []

# Visual elements
ocean = None
land = None
mountains = []
trees = []
clouds = []
sun = None
sun_rays = []
arrows = []
text_elements = []

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(16, 10))
plt.subplots_adjust(left=0.08, bottom=0.25, right=0.68, top=0.95)

# Main visualization axes
ax = plt.axes([0.08, 0.30, 0.58, 0.65])
ax.set_title("Water Cycle Simulator - Junior High Earth Science", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(-2, 2)
ax.set_ylim(-1.5, 1.5)
ax.axis('off')
ax.set_facecolor('#87CEEB')  # Sky blue background

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
             edgecolor="#2196F3", linewidth=2)
)

# -----------------------------
# Controls
# -----------------------------
ax_temp = plt.axes([0.1, 0.18, 0.15, 0.03])
temp_slider = Slider(ax_temp, 'Temp (°C)', 10, 40, valinit=25, valstep=1)

ax_humidity = plt.axes([0.1, 0.14, 0.15, 0.03])
humidity_slider = Slider(ax_humidity, 'Humidity', 0, 100, valinit=50, valstep=5)

ax_wind = plt.axes([0.1, 0.10, 0.15, 0.03])
wind_slider = Slider(ax_wind, 'Wind Speed', 0, 100, valinit=30, valstep=5)

ax_sunlight = plt.axes([0.1, 0.06, 0.15, 0.03])
sunlight_slider = Slider(ax_sunlight, 'Sunlight', 0, 100, valinit=70, valstep=5)

ax_animate = plt.axes([0.3, 0.06, 0.1, 0.04])
btn_animate = Button(ax_animate, 'Animate')

ax_reset = plt.axes([0.42, 0.06, 0.1, 0.04])
btn_reset = Button(ax_reset, 'Reset')

# -----------------------------
# Water Cycle Functions
# -----------------------------
def calculate_evaporation_rate(temp, sunlight, humidity, wind):
    """Calculate evaporation rate based on environmental factors."""
    # Higher temperature increases evaporation
    temp_factor = (temp - 10) / 30.0
    
    # Sunlight provides energy for evaporation
    sun_factor = sunlight / 100.0
    
    # Higher humidity reduces evaporation (air is already saturated)
    humidity_factor = 1.0 - (humidity / 100.0) * 0.5
    
    # Wind increases evaporation by removing saturated air
    wind_factor = 1.0 + (wind / 100.0) * 0.3
    
    rate = temp_factor * sun_factor * humidity_factor * wind_factor * 100
    return max(0, min(100, rate))

def calculate_condensation_rate(temp, humidity):
    """Calculate condensation rate (cloud formation)."""
    # Lower temperature increases condensation
    temp_factor = 1.0 - (temp - 10) / 30.0
    
    # Higher humidity increases condensation
    humidity_factor = humidity / 100.0
    
    rate = temp_factor * humidity_factor * 100
    return max(0, min(100, rate))

def calculate_precipitation_rate(temp, humidity, condensation):
    """Calculate precipitation rate."""
    # Need high condensation for precipitation
    cond_factor = condensation / 100.0
    
    # Higher humidity increases precipitation
    humidity_factor = humidity / 100.0
    
    # Temperature affects whether it's rain or snow
    if temp < 0:
        # Snow
        temp_factor = 1.0
    else:
        # Rain
        temp_factor = 1.0
    
    rate = cond_factor * humidity_factor * temp_factor * 100
    return max(0, min(100, rate))

# -----------------------------
# Visualization Functions
# -----------------------------
def clear_visualization():
    """Clear all visual elements."""
    global ocean, land, mountains, trees, clouds, sun, sun_rays
    global arrows, text_elements, water_particles, cloud_particles, rain_drops, snow_flakes
    
    # Clear patches
    if ocean is not None:
        try:
            ocean.remove()
        except (ValueError, AttributeError):
            pass
        ocean = None
    
    if land is not None:
        try:
            land.remove()
        except (ValueError, AttributeError):
            pass
        land = None
    
    for mountain in mountains:
        try:
            mountain.remove()
        except (ValueError, AttributeError):
            pass
    mountains = []
    
    for tree in trees:
        try:
            tree.remove()
        except (ValueError, AttributeError):
            pass
    trees = []
    
    for cloud in clouds:
        try:
            cloud.remove()
        except (ValueError, AttributeError):
            pass
    clouds = []
    
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
    
    for arrow in arrows:
        try:
            arrow.remove()
        except (ValueError, AttributeError):
            pass
    arrows = []
    
    # Clear text elements
    for text in text_elements:
        try:
            text.remove()
        except (ValueError, AttributeError):
            pass
    text_elements = []
    
    # Clear particles
    water_particles = []
    cloud_particles = []
    rain_drops = []
    snow_flakes = []

def draw_background():
    """Draw the static background elements."""
    global ocean, land, mountains, trees, sun, sun_rays
    
    # Draw ocean (bottom)
    ocean = Rectangle((-2, -1.5), 4, 0.6, facecolor='#4682B4', 
                     edgecolor='#2E4A62', linewidth=2, zorder=1)
    ax.add_patch(ocean)
    
    # Draw land (middle)
    land = Rectangle((-2, -0.9), 4, 0.4, facecolor='#8B7355', 
                    edgecolor='#5C4A37', linewidth=2, zorder=2)
    ax.add_patch(land)
    
    # Draw mountains
    mountain1 = Polygon([(-1.5, -0.9), (-1.2, -0.3), (-0.9, -0.9)], 
                       facecolor='#696969', edgecolor='#2F2F2F', linewidth=1.5, zorder=3)
    mountain2 = Polygon([(-0.6, -0.9), (-0.3, -0.2), (0, -0.9)], 
                       facecolor='#696969', edgecolor='#2F2F2F', linewidth=1.5, zorder=3)
    mountain3 = Polygon([(0.3, -0.9), (0.6, -0.4), (0.9, -0.9)], 
                       facecolor='#696969', edgecolor='#2F2F2F', linewidth=1.5, zorder=3)
    mountains = [mountain1, mountain2, mountain3]
    for mountain in mountains:
        ax.add_patch(mountain)
    
    # Draw trees
    for x_pos in [-1.3, -0.4, 0.5]:
        # Tree trunk
        trunk = Rectangle((x_pos - 0.05, -0.9), 0.1, 0.2, 
                        facecolor='#8B4513', edgecolor='#654321', linewidth=1, zorder=4)
        ax.add_patch(trunk)
        trees.append(trunk)
        
        # Tree leaves (circle)
        leaves = Circle((x_pos, -0.7), 0.15, facecolor='#228B22', 
                       edgecolor='#006400', linewidth=1, zorder=4)
        ax.add_patch(leaves)
        trees.append(leaves)
    
    # Draw sun
    sun = Circle((1.5, 1.2), 0.2, facecolor='#FFD700', 
                edgecolor='#FFA500', linewidth=2, zorder=5)
    ax.add_patch(sun)
    
    # Draw sun rays
    ray_length = 0.15
    for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
        x_start = 1.5 + 0.2 * np.cos(angle)
        y_start = 1.2 + 0.2 * np.sin(angle)
        x_end = 1.5 + (0.2 + ray_length) * np.cos(angle)
        y_end = 1.2 + (0.2 + ray_length) * np.sin(angle)
        ray = FancyArrowPatch((x_start, y_start), (x_end, y_end),
                             arrowstyle='-', color='#FFD700', linewidth=2, 
                             alpha=0.6, zorder=4)
        ax.add_patch(ray)
        sun_rays.append(ray)

def draw_water_cycle():
    """Draw the water cycle visualization."""
    clear_visualization()
    draw_background()
    
    temp = state["temperature"]
    humidity = state["humidity"]
    wind = state["wind_speed"]
    sunlight = state["sunlight"]
    time = state["animation_time"]
    
    # Calculate rates
    evap_rate = calculate_evaporation_rate(temp, sunlight, humidity, wind)
    cond_rate = calculate_condensation_rate(temp, humidity)
    precip_rate = calculate_precipitation_rate(temp, humidity, cond_rate)
    
    # Draw evaporation (water vapor rising from ocean)
    if evap_rate > 10:
        num_particles = int(evap_rate / 10)
        for i in range(min(num_particles, 8)):
            x = -1.5 + (i % 4) * 0.4 + np.sin(time * 2 + i) * 0.1
            y = -1.2 + (time * 0.3) % 1.0 + (i // 4) * 0.2
            if y < 0.5:  # Only show particles below clouds
                particle = Circle((x, y), 0.03, facecolor='#E0F6FF', 
                                edgecolor='#87CEEB', linewidth=0.5, 
                                alpha=0.7, zorder=6)
                ax.add_patch(particle)
                water_particles.append(particle)
    
    # Draw transpiration (water vapor from trees)
    if evap_rate > 10:
        for i, x_pos in enumerate([-1.3, -0.4, 0.5]):
            if np.random.random() < evap_rate / 200:
                y = -0.7 + (time * 0.2) % 0.8
                if y < 0.3:
                    particle = Circle((x_pos + np.sin(time + i) * 0.05, y), 0.025, 
                                    facecolor='#E0F6FF', edgecolor='#87CEEB', 
                                    linewidth=0.5, alpha=0.6, zorder=6)
                    ax.add_patch(particle)
                    water_particles.append(particle)
    
    # Draw clouds
    if cond_rate > 20:
        cloud_y = 0.8
        num_clouds = min(3, int(cond_rate / 30))
        
        for i in range(num_clouds):
            cloud_x = -1.0 + i * 1.0 + np.sin(time * 0.5 + i) * 0.2
            # Draw cloud as overlapping circles
            cloud_parts = []
            for j in range(3):
                offset_x = (j - 1) * 0.15
                cloud_circle = Ellipse((cloud_x + offset_x, cloud_y), 0.25, 0.15,
                                      facecolor='#FFFFFF', edgecolor='#CCCCCC', 
                                      linewidth=1, alpha=0.8, zorder=7)
                ax.add_patch(cloud_circle)
                cloud_parts.append(cloud_circle)
            clouds.extend(cloud_parts)
    
    # Draw precipitation (rain or snow)
    if precip_rate > 30:
        is_snow = temp < 0
        num_drops = int(precip_rate / 5)
        
        for i in range(min(num_drops, 20)):
            if is_snow:
                # Snow flakes
                x = -1.5 + (i % 10) * 0.3 + np.sin(time * 2 + i) * 0.1
                y = 0.7 - (time * 0.5 + i * 0.05) % 1.4
                if y > -0.9:
                    # Draw snowflake as small star
                    from matplotlib.lines import Line2D
                    angles = np.linspace(0, 2*np.pi, 6, endpoint=False)
                    for angle in angles:
                        x_end = x + 0.02 * np.cos(angle)
                        y_end = y + 0.02 * np.sin(angle)
                        line = Line2D([x, x_end], [y, y_end],
                                     color='white', linewidth=1, alpha=0.8, zorder=8)
                        ax.add_line(line)
                        snow_flakes.append(line)
            else:
                # Rain drops
                x = -1.5 + (i % 10) * 0.3 + np.sin(time * 2 + i) * 0.1
                y = 0.7 - (time * 0.8 + i * 0.05) % 1.4
                if y > -0.9:
                    drop = FancyArrowPatch((x, y), (x, y - 0.05),
                                          arrowstyle='->', color='#4169E1', 
                                          linewidth=1.5, alpha=0.7, zorder=8)
                    ax.add_patch(drop)
                    rain_drops.append(drop)
    
    # Draw arrows showing cycle direction
    # Evaporation arrow (ocean to sky)
    if evap_rate > 10:
        arrow1 = FancyArrowPatch((-1.0, -1.2), (-0.8, 0.3),
                               arrowstyle='->', mutation_scale=20,
                               color='#87CEEB', linewidth=2, alpha=0.5, zorder=5)
        ax.add_patch(arrow1)
        arrows.append(arrow1)
        
        label1 = ax.text(-0.9, -0.4, 'Evaporation', ha='center', va='center',
                        fontsize=8, color='#4169E1', fontweight='bold', zorder=9)
        text_elements.append(label1)
    
    # Condensation arrow (vapor to clouds)
    if cond_rate > 20:
        arrow2 = FancyArrowPatch((-0.5, 0.5), (-0.3, 0.75),
                               arrowstyle='->', mutation_scale=20,
                               color='#87CEEB', linewidth=2, alpha=0.5, zorder=5)
        ax.add_patch(arrow2)
        arrows.append(arrow2)
        
        label2 = ax.text(-0.4, 0.6, 'Condensation', ha='center', va='center',
                        fontsize=8, color='#4169E1', fontweight='bold', zorder=9)
        text_elements.append(label2)
    
    # Precipitation arrow (clouds to ground)
    if precip_rate > 30:
        arrow3 = FancyArrowPatch((0.0, 0.7), (0.0, -0.5),
                               arrowstyle='->', mutation_scale=20,
                               color='#4169E1', linewidth=2, alpha=0.6, zorder=5)
        ax.add_patch(arrow3)
        arrows.append(arrow3)
        
        label3 = ax.text(0.15, 0.1, 'Precipitation', ha='center', va='center',
                        fontsize=8, color='#4169E1', fontweight='bold', zorder=9)
        text_elements.append(label3)
    
    # Runoff arrow (ground to ocean)
    arrow4 = FancyArrowPatch((0.5, -0.7), (-1.0, -1.0),
                           arrowstyle='->', mutation_scale=20,
                           color='#4169E1', linewidth=2, alpha=0.5, zorder=5)
    ax.add_patch(arrow4)
    arrows.append(arrow4)
    
    label4 = ax.text(-0.2, -0.85, 'Runoff', ha='center', va='center',
                    fontsize=8, color='#4169E1', fontweight='bold', zorder=9)
    text_elements.append(label4)
    
    # Update info panel
    update_info_panel(temp, humidity, wind, sunlight, evap_rate, cond_rate, precip_rate)

def update_info_panel(temp, humidity, wind, sunlight, evap_rate, cond_rate, precip_rate):
    """Update the information panel."""
    precip_type = "Snow" if temp < 0 else "Rain"
    
    info = f"""
╔═══════════════════════════════╗
║     WATER CYCLE SIMULATOR     ║
╚═══════════════════════════════╝

ENVIRONMENTAL CONDITIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Temperature: {temp}°C
Humidity: {humidity}%
Wind Speed: {wind}%
Sunlight: {sunlight}%

WATER CYCLE PROCESSES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Evaporation Rate: {evap_rate:.1f}%
  • Water turns to vapor
  • Driven by heat & sunlight

Condensation Rate: {cond_rate:.1f}%
  • Vapor forms clouds
  • Requires cooling & humidity

Precipitation Rate: {precip_rate:.1f}%
  • Type: {precip_type}
  • Water returns to Earth

WATER CYCLE STAGES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Evaporation (Ocean → Vapor)
2. Transpiration (Plants → Vapor)
3. Condensation (Vapor → Clouds)
4. Precipitation (Clouds → {precip_type})
5. Collection (Runoff → Ocean)

TIP: Increase temperature and
sunlight to see more evaporation!
"""
    
    info_text.set_text(info)

# -----------------------------
# Animation
# -----------------------------
animation = None

def animate(frame):
    """Animation function."""
    if state["is_animating"]:
        state["animation_time"] += 0.05 * state["speed"]
        draw_water_cycle()
    return []

# -----------------------------
# Event Handlers
# -----------------------------
def on_temp_change(val):
    """Handle temperature slider change."""
    state["temperature"] = val
    if not state["is_animating"]:
        draw_water_cycle()

def on_humidity_change(val):
    """Handle humidity slider change."""
    state["humidity"] = val
    if not state["is_animating"]:
        draw_water_cycle()

def on_wind_change(val):
    """Handle wind speed slider change."""
    state["wind_speed"] = val
    if not state["is_animating"]:
        draw_water_cycle()

def on_sunlight_change(val):
    """Handle sunlight slider change."""
    state["sunlight"] = val
    if not state["is_animating"]:
        draw_water_cycle()

def on_animate(_):
    """Toggle animation."""
    global animation
    state["is_animating"] = not state["is_animating"]
    
    if state["is_animating"]:
        btn_animate.label.set_text("Stop")
        # Stop any existing animation first
        if animation is not None:
            try:
                animation.event_source.stop()
            except AttributeError:
                pass
        # Create new animation
        animation = FuncAnimation(fig, animate, interval=50, 
                                 blit=False, cache_frame_data=False)
    else:
        btn_animate.label.set_text("Animate")
        if animation is not None:
            try:
                animation.event_source.stop()
            except AttributeError:
                pass
    fig.canvas.draw_idle()

def on_reset(_):
    """Reset to initial state."""
    global animation
    # Stop animation first
    state["is_animating"] = False
    if animation is not None:
        try:
            animation.event_source.stop()
        except AttributeError:
            pass
        animation = None
    # Reset animation time
    state["animation_time"] = 0.0
    # Update button
    btn_animate.label.set_text("Animate")
    # Redraw visualization
    draw_water_cycle()
    fig.canvas.draw_idle()

# Wire up events
temp_slider.on_changed(on_temp_change)
humidity_slider.on_changed(on_humidity_change)
wind_slider.on_changed(on_wind_change)
sunlight_slider.on_changed(on_sunlight_change)
btn_animate.on_clicked(on_animate)
btn_reset.on_clicked(on_reset)

# Initial visualization
draw_water_cycle()
plt.show()

