# Spec: HEMS Optimizer

## Purpose
The Optimizer uses Linear Programming (LP) to schedule the optimal charging and discharging of the household battery. It minimizes electricity cost by leveraging a 3-zone tariff (Night, Semi-Peak, Peak), solar generation, and load forecasts over a 24-hour horizon.

## Tariff Zones
- **Night:** Low cost (e.g., 23:00 - 07:00)
- **Semi-Peak:** Medium cost (e.g., 07:00 - 09:00, 17:00 - 20:00)
- **Peak:** High cost (e.g., 09:00 - 17:00, 20:00 - 23:00)
*Note: Time ranges can be configurable but will have 3 distinct price levels.*

## Constraints
1. **Battery Capacity:** The battery state of charge (SoC) must stay within limits (e.g., 0 to Max Capacity).
2. **Charge/Discharge Rates:** Maximum power limits for charging and discharging per hour.
3. **Energy Balance:** Load + Battery Charge = Solar + Battery Discharge + Grid Import.
4. **Grid Export (Optional):** May or may not allow exporting to the grid (we assume no export or minimal export logic unless specified).

## Contract
- **Endpoint:** `POST /hems/optimize`
- **Request (JSON):**
  - `load_forecast: list[float]` (24 hourly load values)
  - `solar_forecast: list[float]` (24 hourly solar values)
  - `battery_capacity: float` (Max capacity in kWh)
  - `initial_soc: float` (Current state of charge in kWh)
  - `max_charge_rate: float` (Max charging power in kW)
  - `max_discharge_rate: float` (Max discharging power in kW)
  - `prices: list[float]` (24 hourly electricity prices)
- **Response (JSON):**
  - `schedule: list[dict]` (24 items, each with `hour`, `charge`, `discharge`, `grid_import`, `battery_soc`)
  - `total_cost: float` (Total optimized cost for the 24 hours)

## Internal Module (`optimizer.py`)
- Should formulate the LP problem using an optimization library (e.g., `scipy.optimize` or `pulp`).
- Minimized objective function: `Sum(Grid Import(t) * Price(t))` over t=0..23.

## Acceptance Tests
- **Given** cheap night prices and high peak prices, **When** optimizing, **Then** battery charges at night and discharges during the peak.
- **Given** high solar generation in the afternoon, **When** optimizing, **Then** battery charges from excess solar instead of the grid.
- **Given** a 5kWh battery, **When** optimizing, **Then** the state of charge never exceeds 5kWh or drops below 0.
