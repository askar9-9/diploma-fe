import pytest
from app.optimizer import optimize_schedule

def test_optimizer_charges_at_night_discharges_at_peak():
    # 24 hours of data
    load_forecast = [1.0] * 24
    solar_forecast = [0.0] * 24
    
    # Prices: Night (hours 0-7) = 1.0, Semi-Peak (hours 8-17) = 2.0, Peak (hours 18-23) = 5.0
    prices = [1.0]*8 + [2.0]*10 + [5.0]*6
    
    # Battery parameters
    battery_capacity = 10.0
    initial_soc = 0.0
    max_charge_rate = 5.0
    max_discharge_rate = 5.0
    
    schedule, total_cost = optimize_schedule(
        load_forecast=load_forecast,
        solar_forecast=solar_forecast,
        battery_capacity=battery_capacity,
        initial_soc=initial_soc,
        max_charge_rate=max_charge_rate,
        max_discharge_rate=max_discharge_rate,
        prices=prices
    )
    
    assert len(schedule) == 24
    
    # Should charge at night when prices are 1.0
    # Let's check that battery_soc increases during night
    assert schedule[0]['charge'] > 0
    assert schedule[18]['discharge'] > 0 # Should discharge during peak (hours 18-23)
    
def test_optimizer_respects_battery_limits():
    load_forecast = [1.0] * 24
    solar_forecast = [0.0] * 24
    prices = [1.0] * 24
    
    schedule, _ = optimize_schedule(
        load_forecast=load_forecast,
        solar_forecast=solar_forecast,
        battery_capacity=5.0,
        initial_soc=3.0,
        max_charge_rate=2.0,
        max_discharge_rate=2.0,
        prices=prices
    )
    
    for step in schedule:
        assert 0.0 <= step['battery_soc'] <= 5.0
        assert step['charge'] <= 2.0
        assert step['discharge'] <= 2.0

def test_optimizer_uses_solar():
    load_forecast = [2.0] * 24
    # Huge solar spike at noon (hour 12)
    solar_forecast = [0.0] * 12 + [10.0] + [0.0] * 11
    prices = [1.0] * 24
    
    schedule, _ = optimize_schedule(
        load_forecast=load_forecast,
        solar_forecast=solar_forecast,
        battery_capacity=10.0,
        initial_soc=0.0,
        max_charge_rate=5.0,
        max_discharge_rate=5.0,
        prices=prices
    )
    
    # At hour 12, we have 10 solar and 2 load. The remaining 8 can charge the battery.
    # Max charge rate is 5, so it should charge by 5.
    assert schedule[12]['charge'] > 0.0
