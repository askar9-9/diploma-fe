from __future__ import annotations


DEVICE_POWER_WATTS: dict[str, float] = {
    "ceiling_light": 60.0,
    "bedside_light": 10.0,
    "thermostat": 1500.0,
    "tv_on": 120.0,
}


SCENE_DEVICE_STATES: dict[str, dict[str, float]] = {
    "day": {
        "ceiling_light": 1.0,
        "bedside_light": 0.0,
        "thermostat": 1.0,
        "tv_on": 0.0,
    },
    "night": {
        "ceiling_light": 0.0,
        "bedside_light": 1.0,
        "thermostat": 0.7,
        "tv_on": 0.0,
    },
    "away": {
        "ceiling_light": 0.0,
        "bedside_light": 0.0,
        "thermostat": 0.3,
        "tv_on": 0.0,
    },
    "movie": {
        "ceiling_light": 0.0,
        "bedside_light": 0.0,
        "thermostat": 1.0,
        "tv_on": 1.0,
    },
}


def calculate_consumption_wh(scene: str) -> float:
    """Потребление в Вт·ч за 1 час для данной сцены."""
    states = SCENE_DEVICE_STATES.get(scene, SCENE_DEVICE_STATES["away"])
    return sum(
        states.get(device, 0.0) * watts for device, watts in DEVICE_POWER_WATTS.items()
    )


def predict_scene_for_hour(hour: int, weekday: int, classifier) -> tuple[str, float]:
    """
    Предсказывает сцену для заданного часа используя классификатор.
    Возвращает (scenario, confidence).
    """
    if 0 <= hour <= 6:
        motion_hall, motion_living, tv_on, light, temp, idle = 0, 0, 0, 0.0, 18.0, 240
    elif 7 <= hour <= 8:
        motion_hall, motion_living, tv_on, light, temp, idle = 1, 1, 0, 90.0, 22.0, 5
    elif 9 <= hour <= 17:
        motion_hall, motion_living, tv_on, light, temp, idle = 1, 0, 0, 80.0, 22.0, 15
    elif 18 <= hour <= 22:
        motion_hall, motion_living, tv_on, light, temp, idle = 0, 1, 1, 20.0, 22.0, 10
    else:
        motion_hall, motion_living, tv_on, light, temp, idle = 0, 0, 0, 10.0, 20.0, 60

    fv = {
        "hour_of_day": hour,
        "weekday": weekday,
        "motion_hall": motion_hall,
        "motion_living": motion_living,
        "temperature": temp,
        "light_level": light,
        "tv_on": tv_on,
        "minutes_idle": idle,
    }

    try:
        result = classifier.predict(fv)
        return result.scenario, result.confidence
    except Exception:
        if 0 <= hour <= 6:
            return "away", 0.95
        if 7 <= hour <= 17:
            return "day", 0.90
        if 18 <= hour <= 22:
            return "movie", 0.75
        return "night", 0.90


class EnergyForecaster:
    def forecast_24h(self, classifier, current_hour: int, weekday: int) -> list[dict]:
        """
        Прогноз потребления на 24 часа начиная с current_hour.
        Возвращает список из 24 точек.
        """
        results = []
        for offset in range(24):
            hour = (current_hour + offset) % 24
            scenario, confidence = predict_scene_for_hour(hour, weekday, classifier)
            scene_devices = SCENE_DEVICE_STATES.get(scenario, SCENE_DEVICE_STATES["away"])
            consumption_wh = calculate_consumption_wh(scenario)

            results.append(
                {
                    "hour": hour,
                    "offset_hours": offset,
                    "scenario": scenario,
                    "confidence": round(confidence, 3),
                    "consumption_wh": round(consumption_wh, 1),
                    "consumption_kwh": round(consumption_wh / 1000, 4),
                    "devices": dict(scene_devices),
                }
            )
        return results

    def daily_total_kwh(self, forecast: list[dict]) -> float:
        """Суммарное потребление за сутки в кВт·ч."""
        return round(sum(point["consumption_kwh"] for point in forecast), 3)

    def peak_hour(self, forecast: list[dict]) -> dict:
        """Час с максимальным потреблением."""
        return max(forecast, key=lambda point: point["consumption_wh"])

    def recommendations(self, forecast: list[dict]) -> list[str]:
        """Простые рекомендации по экономии."""
        tips: list[str] = []
        total = self.daily_total_kwh(forecast)
        if total > 20:
            tips.append(
                "Высокое суточное потребление. Снизьте уставку термостата на 1-2°C."
            )

        peak = self.peak_hour(forecast)
        if peak["consumption_wh"] > 1500:
            tips.append(
                f"Пик потребления в {peak['hour']}:00 ({peak['consumption_wh']}Вт). "
                "Перенесите часть нагрузки."
            )

        away_hours = [point for point in forecast if point["scenario"] == "away"]
        if not away_hours:
            tips.append(
                "Дом занят круглосуточно — убедитесь что термостат снижается при отсутствии."
            )

        if not tips:
            tips.append("Потребление в норме. Продолжайте в том же режиме.")
        return tips
