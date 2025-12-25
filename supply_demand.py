import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
import matplotlib.patches as mpatches

# -----------------------------
# Supply and Demand Simulator
# For Junior High School Social Science
# -----------------------------

# State
state = {
    "demand": 50,      # Demand level (0-100)
    "supply": 50,      # Supply level (0-100)
    "base_price": 10.0  # Base price
}

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(14, 9))
plt.subplots_adjust(left=0.08, bottom=0.25, right=0.68, top=0.95)

# Main graph axes (left side, larger)
ax = plt.axes([0.08, 0.30, 0.58, 0.65])
ax.set_title("Supply and Demand Simulator - Junior High Social Science", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Quantity", fontsize=12, fontweight='bold')
ax.set_ylabel("Price ($)", fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_facecolor('#f8f9fa')

# Graph elements
supply_line = None
demand_line = None
equilibrium_point = None
equilibrium_text = None
price_display = None
surplus_patch = None
shortage_patch = None

# Info panel (right side)
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
             edgecolor="#3498db", linewidth=2)
)

# -----------------------------
# Supply and Demand Functions
# -----------------------------
def calculate_price(demand, supply):
    """Calculate equilibrium price based on supply and demand."""
    # Simple model: price increases with demand, decreases with supply
    # Equilibrium price = base_price * (demand / supply)
    if supply == 0:
        supply = 0.1  # Avoid division by zero
    price = state["base_price"] * (demand / supply)
    return max(1.0, min(50.0, price))  # Clamp between $1 and $50

def calculate_quantity(demand, supply):
    """Calculate equilibrium quantity."""
    # Quantity is where supply and demand meet
    # Average of supply and demand, scaled
    return (demand + supply) / 2

def get_demand_curve(demand_level, price_range):
    """Generate demand curve points."""
    # Demand curve slopes downward: higher price = lower quantity demanded
    # Q = demand_level * (max_price - price) / max_price
    max_price = price_range[-1]
    quantities = []
    for price in price_range:
        q = demand_level * (max_price - price) / max_price
        quantities.append(max(0, q))
    return np.array(quantities)

def get_supply_curve(supply_level, price_range):
    """Generate supply curve points."""
    # Supply curve slopes upward: higher price = higher quantity supplied
    # Q = supply_level * price / max_price
    max_price = price_range[-1]
    quantities = []
    for price in price_range:
        q = supply_level * price / max_price
        quantities.append(max(0, q))
    return np.array(quantities)

# -----------------------------
# Visualization Functions
# -----------------------------
def update_graph():
    """Update the supply and demand graph."""
    global supply_line, demand_line, equilibrium_point, equilibrium_text, price_display
    global surplus_patch, shortage_patch
    
    # Clear previous elements
    if supply_line is not None:
        try:
            if isinstance(supply_line, list):
                for line in supply_line:
                    line.remove()
            else:
                supply_line.remove()
        except (ValueError, AttributeError):
            pass
        supply_line = None
    
    if demand_line is not None:
        try:
            if isinstance(demand_line, list):
                for line in demand_line:
                    line.remove()
            else:
                demand_line.remove()
        except (ValueError, AttributeError):
            pass
        demand_line = None
    
    if equilibrium_point is not None:
        try:
            if isinstance(equilibrium_point, list):
                for point in equilibrium_point:
                    point.remove()
            else:
                equilibrium_point.remove()
        except (ValueError, AttributeError):
            pass
        equilibrium_point = None
    
    if equilibrium_text is not None:
        try:
            equilibrium_text.remove()
        except (ValueError, AttributeError):
            pass
        equilibrium_text = None
    
    if price_display is not None:
        try:
            price_display.remove()
        except (ValueError, AttributeError):
            pass
        price_display = None
    
    if surplus_patch is not None:
        try:
            surplus_patch.remove()
        except (ValueError, AttributeError):
            pass
        surplus_patch = None
    
    if shortage_patch is not None:
        try:
            shortage_patch.remove()
        except (ValueError, AttributeError):
            pass
        shortage_patch = None
    
    # Also clear any text elements that might be leftover (but keep axis labels)
    texts_to_remove = []
    for text in ax.texts:
        if text not in [ax.title, ax.xaxis.label, ax.yaxis.label]:
            texts_to_remove.append(text)
    for text in texts_to_remove:
        try:
            text.remove()
        except (ValueError, AttributeError):
            pass
    
    demand_level = state["demand"]
    supply_level = state["supply"]
    
    # Price range for the graph
    price_range = np.linspace(1, 50, 100)
    
    # Get curves
    demand_q = get_demand_curve(demand_level, price_range)
    supply_q = get_supply_curve(supply_level, price_range)
    
    # Find equilibrium (where curves intersect)
    diff = np.abs(demand_q - supply_q)
    eq_idx = np.argmin(diff)
    eq_price = price_range[eq_idx]
    eq_quantity = (demand_q[eq_idx] + supply_q[eq_idx]) / 2
    
    # Set axes limits
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 55)
    
    # Draw demand curve (downward sloping, red)
    demand_line_obj = ax.plot(demand_q, price_range, 'r-', linewidth=3, 
                              label='Demand', alpha=0.8)
    demand_line = demand_line_obj[0] if isinstance(demand_line_obj, list) else demand_line_obj
    
    # Draw supply curve (upward sloping, blue)
    supply_line_obj = ax.plot(supply_q, price_range, 'b-', linewidth=3, 
                              label='Supply', alpha=0.8)
    supply_line = supply_line_obj[0] if isinstance(supply_line_obj, list) else supply_line_obj
    
    # Mark equilibrium point
    eq_point_obj = ax.plot(eq_quantity, eq_price, 'go', 
                           markersize=15, markeredgecolor='darkgreen',
                           markeredgewidth=2, zorder=5, label='Equilibrium')
    equilibrium_point = eq_point_obj[0] if isinstance(eq_point_obj, list) else eq_point_obj
    
    # Equilibrium label
    equilibrium_text = ax.text(eq_quantity + 5, eq_price + 2,
                              f'Eq: Q={eq_quantity:.1f}, P=${eq_price:.2f}',
                              fontsize=10, fontweight='bold',
                              bbox=dict(boxstyle="round,pad=0.5", 
                                       facecolor="yellow", alpha=0.9),
                              zorder=6)
    
    # Price display
    price_display = ax.text(5, 50, f'Price: ${eq_price:.2f}',
                           fontsize=16, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.8", 
                                    facecolor="lightgreen", alpha=0.9,
                                    edgecolor="darkgreen", linewidth=2),
                           zorder=7)
    
    # Show surplus or shortage
    if supply_q[eq_idx] > demand_q[eq_idx]:
        # Surplus (supply > demand at equilibrium price)
        surplus = supply_q[eq_idx] - demand_q[eq_idx]
        # Draw surplus area
        surplus_x = [demand_q[eq_idx], supply_q[eq_idx], supply_q[eq_idx], demand_q[eq_idx]]
        surplus_y = [eq_price, eq_price, eq_price + 2, eq_price + 2]
        surplus_patch = Polygon(list(zip(surplus_x, surplus_y)), 
                               closed=True, facecolor='lightblue', 
                               alpha=0.5, edgecolor='blue', linewidth=2)
        ax.add_patch(surplus_patch)
        ax.text((demand_q[eq_idx] + supply_q[eq_idx])/2, eq_price + 3,
               f'Surplus: {surplus:.1f}',
               ha='center', fontsize=9, fontweight='bold', color='blue')
    elif demand_q[eq_idx] > supply_q[eq_idx]:
        # Shortage (demand > supply at equilibrium price)
        shortage = demand_q[eq_idx] - supply_q[eq_idx]
        # Draw shortage area
        shortage_x = [supply_q[eq_idx], demand_q[eq_idx], demand_q[eq_idx], supply_q[eq_idx]]
        shortage_y = [eq_price, eq_price, eq_price - 2, eq_price - 2]
        shortage_patch = Polygon(list(zip(shortage_x, shortage_y)), 
                                closed=True, facecolor='lightcoral', 
                                alpha=0.5, edgecolor='red', linewidth=2)
        ax.add_patch(shortage_patch)
        ax.text((demand_q[eq_idx] + supply_q[eq_idx])/2, eq_price - 3,
               f'Shortage: {shortage:.1f}',
               ha='center', fontsize=9, fontweight='bold', color='red')
    
    # Legend
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Update info panel
    update_info(eq_price, eq_quantity, demand_level, supply_level)
    
    fig.canvas.draw_idle()

def update_info(price, quantity, demand, supply):
    """Update information panel."""
    info = (
        f"╔═══════════════════════════╗\n"
        f"║ SUPPLY & DEMAND          ║\n"
        f"╚═══════════════════════════╝\n\n"
        f"[*] Current Market:\n"
        f"  Price: ${price:.2f}\n"
        f"  Quantity: {quantity:.1f} units\n\n"
        f"[+] Demand Level: {demand:.0f}\n"
        f"  Higher = More buyers\n"
        f"  Want to buy more\n\n"
        f"[+] Supply Level: {supply:.0f}\n"
        f"  Higher = More sellers\n"
        f"  Want to sell more\n\n"
        f"[!] Key Concepts:\n"
        f"  • High demand → Higher price\n"
        f"  • High supply → Lower price\n"
        f"  • Equilibrium = Balance point\n"
        f"  • Red line = Demand\n"
        f"  • Blue line = Supply\n"
        f"  • Green dot = Equilibrium"
    )
    info_text.set_text(info)

# -----------------------------
# Controls
# -----------------------------
# Demand slider
ax_demand = plt.axes([0.08, 0.20, 0.35, 0.03])
demand_slider = Slider(ax_demand, "Demand", 10, 100, valinit=50, valstep=5)

# Supply slider
ax_supply = plt.axes([0.08, 0.15, 0.35, 0.03])
supply_slider = Slider(ax_supply, "Supply", 10, 100, valinit=50, valstep=5)

# Buttons
ax_reset = plt.axes([0.45, 0.15, 0.10, 0.04])
btn_reset = Button(ax_reset, "Reset")

ax_example1 = plt.axes([0.45, 0.20, 0.12, 0.04])
btn_example1 = Button(ax_example1, "High Demand")

ax_example2 = plt.axes([0.58, 0.20, 0.12, 0.04])
btn_example2 = Button(ax_example2, "High Supply")

# -----------------------------
# Event Handlers
# -----------------------------
def on_demand_change(val):
    """Handle demand slider change."""
    state["demand"] = val
    update_graph()

def on_supply_change(val):
    """Handle supply slider change."""
    state["supply"] = val
    update_graph()

def on_reset(_):
    """Reset to default values."""
    state["demand"] = 50
    state["supply"] = 50
    demand_slider.reset()
    supply_slider.reset()
    update_graph()

def on_high_demand(_):
    """Set high demand scenario."""
    state["demand"] = 80
    state["supply"] = 30
    demand_slider.set_val(80)
    supply_slider.set_val(30)
    update_graph()

def on_high_supply(_):
    """Set high supply scenario."""
    state["demand"] = 30
    state["supply"] = 80
    demand_slider.set_val(30)
    supply_slider.set_val(80)
    update_graph()

# Wire up events
demand_slider.on_changed(on_demand_change)
supply_slider.on_changed(on_supply_change)
btn_reset.on_clicked(on_reset)
btn_example1.on_clicked(on_high_demand)
btn_example2.on_clicked(on_high_supply)

# Initial graph
update_graph()
plt.show()

