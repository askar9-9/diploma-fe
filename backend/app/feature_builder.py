from datetime import datetime
from typing import Optional, Union


def build_feature_vector(
    devices: dict,
    simulated_time: Optional[datetime] = None,
) -> dict[str, Union[float, int]]:
    moment = simulated_time or datetime.utcnow()

    motion_hall = int(devices.get("motion_hall", {}).get("state", 0.0))
    motion_living = int(devices.get("motion_living", {}).get("state", 0.0))

    return {
        "hour_of_day": moment.hour,
        "weekday": moment.weekday(),
        "motion_hall": motion_hall,
        "motion_living": motion_living,
        "temperature": float(devices.get("temperature", {}).get("state", 0.0)),
        "light_level": float(devices.get("light_level", {}).get("state", 0.0)),
        "tv_on": int(devices.get("tv_on", {}).get("state", 0.0)),
        "minutes_idle": 0 if (motion_hall or motion_living) else 60,
    }
