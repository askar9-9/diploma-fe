# Spec: Energy Forecast (Load and Solar)

## Purpose
The ML service provides 24-hour predictions for household energy consumption (Load) and solar energy generation (Solar). These predictions are essential for the optimization engine to schedule battery charging and discharging.

## Features
- **Load Forecaster:** Predicts household power consumption (kWh) for the next 24 hours based on historical data, weather, day of the week, and time of day.
- **Solar Forecaster:** Predicts solar power generation (kWh) for the next 24 hours based on solar irradiance, cloud cover, and time of day (no generation during the night).

## Contracts
- The forecasters should be exposed as internal Python modules/classes (`forecasters.py`) and do not necessarily need separate API endpoints if they are primarily used by the optimizer. 
- However, if exposed via the HEMS Engine API, they could be fetched alongside optimization results.

### Internal API (`forecasters.py`)
- `predict_load(history: list[float], day_of_week: int, current_hour: int) -> list[float]`
  - Returns a list of 24 floats representing predicted load (kWh) for the next 24 hours.
- `predict_solar(weather_forecast: list[dict], current_hour: int) -> list[float]`
  - Returns a list of 24 floats representing predicted solar generation (kWh) for the next 24 hours.

## Acceptance Tests
- **Given** historical load data, **When** predicting load, **Then** it returns exactly 24 hourly predictions.
- **Given** night time hours, **When** predicting solar generation, **Then** it returns 0 for those hours.
- **Given** day time hours with sunny weather, **When** predicting solar generation, **Then** it returns positive values.
