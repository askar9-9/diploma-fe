import numpy as np
from scipy.optimize import linprog

def optimize_schedule(
    load_forecast: list[float],
    solar_forecast: list[float],
    battery_capacity: float,
    initial_soc: float,
    max_charge_rate: float,
    max_discharge_rate: float,
    prices: list[float]
) -> tuple[list[dict], float]:
    """
    Optimizes the battery schedule using Linear Programming.
    """
    n = 24
    
    # Variables order:
    # 0..23: charge (c)
    # 24..47: discharge (d)
    # 48..71: soc at end of hour (s)
    # 72..95: grid import (g)
    
    # Objective function
    c_obj = np.zeros(4 * n)
    c_obj[72:96] = prices
    
    # Bounds
    bounds = []
    for _ in range(n): bounds.append((0, max_charge_rate))
    for _ in range(n): bounds.append((0, max_discharge_rate))
    for _ in range(n): bounds.append((0, battery_capacity))
    for _ in range(n): bounds.append((0, None))
    
    A_eq = []
    b_eq = []
    
    # SOC balance
    for t in range(n):
        row = np.zeros(4 * n)
        row[t] = -1.0          # -c[t]
        row[24 + t] = 1.0      # +d[t]
        row[48 + t] = 1.0      # +s[t+1]
        
        if t == 0:
            A_eq.append(row)
            b_eq.append(initial_soc)
        else:
            row[48 + t - 1] = -1.0 # -s[t]
            A_eq.append(row)
            b_eq.append(0.0)
            
    # Energy balance (A_ub * x <= b_ub)
    # c[t] - d[t] - g[t] <= solar[t] - load[t]
    A_ub = []
    b_ub = []
    for t in range(n):
        row = np.zeros(4 * n)
        row[t] = 1.0          # c[t]
        row[24 + t] = -1.0    # -d[t]
        row[72 + t] = -1.0    # -g[t]
        
        A_ub.append(row)
        b_ub.append(max(0.0, solar_forecast[t]) - load_forecast[t])
        
    res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if not res.success:
        # Fallback to empty schedule or zero operation if solver fails
        schedule = []
        soc = initial_soc
        cost = 0.0
        for t in range(n):
            g = max(0.0, load_forecast[t] - solar_forecast[t])
            schedule.append({
                "hour": t,
                "charge": 0.0,
                "discharge": 0.0,
                "grid_import": g,
                "battery_soc": soc
            })
            cost += g * prices[t]
        return schedule, cost

    x = res.x
    charges = x[0:24]
    discharges = x[24:48]
    socs = x[48:72]
    grids = x[72:96]
    
    schedule = []
    for t in range(n):
        schedule.append({
            "hour": t,
            "charge": round(charges[t], 3),
            "discharge": round(discharges[t], 3),
            "grid_import": round(grids[t], 3),
            "battery_soc": round(socs[t], 3)
        })
        
    return schedule, res.fun
