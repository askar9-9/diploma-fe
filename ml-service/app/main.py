from datetime import datetime

from fastapi import FastAPI

from app.classifier import SceneClassifier
from app.forecasters import (
    get_lgbm_forecaster,
    LSTMForecaster,
    build_fallback_history,
    predict_solar,
)
from app.optimizer import optimize_schedule
from app.schemas import (
    ClassifyRequest,
    ClassifyResponse,
    OptimizeRequest,
    OptimizeResponse,
)

app = FastAPI(title="HEMS ML Service")
lgbm = get_lgbm_forecaster()
lstm = LSTMForecaster()
scene_classifier = SceneClassifier()

NIGHT_PRICE = 9.0
DAY_PRICE = 16.0


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _get_tariff(hour: int) -> tuple[str, float]:
    if hour >= 22 or hour < 7:
        return "night", NIGHT_PRICE
    return "day", DAY_PRICE


def _get_status_recommendation(
    hour: int,
    month: int,
) -> tuple[str, str]:
    solar_now = predict_solar(hour, month)[0]
    tariff_zone, _ = _get_tariff(hour)

    if tariff_zone == "night":
        return (
            "charge",
            "Ночной тариф 9 тг/кВт·ч: выгодно заряжать аккумулятор и переносить "
            "энергоемкие задачи на ночные часы.",
        )

    if 18 <= hour < 22:
        return (
            "discharge",
            "Вечерний пик нагрузки при дневном тарифе 16 тг/кВт·ч: используйте "
            "аккумулятор для снижения покупки энергии из сети.",
        )

    if solar_now > 0.0:
        return (
            "charge",
            "Доступна солнечная генерация: направляйте излишки на заряд батареи "
            "или запуск бытовых нагрузок днем.",
        )

    return (
        "idle",
        "Текущий период без выраженной выгоды для заряда или разряда. Держите "
        "аккумулятор в резерве до ночного тарифа или вечернего пика.",
    )


@app.get("/hems/forecast")
def hems_forecast() -> dict:
    now = datetime.now()
    load_forecast = lgbm.predict_load(now.hour, now.weekday())
    if lstm.is_ready:
        lstm_load = lstm.predict_load(build_fallback_history(now.hour))
        load_forecast = [round((a + b) / 2, 3) for a, b in zip(load_forecast, lstm_load)]
    solar_forecast = predict_solar(now.hour, now.month)

    return {
        "load_forecast": [round(float(v), 3) for v in load_forecast],
        "solar_forecast": [round(float(v), 3) for v in solar_forecast],
        "hours": list(range(24)),
    }


@app.get("/hems/status")
def hems_status() -> dict:
    now = datetime.now()
    tariff_zone, tariff_price = _get_tariff(now.hour)
    optimizer_action, recommendation = _get_status_recommendation(now.hour, now.month)

    return {
        "current_hour": now.hour,
        "tariff_zone": tariff_zone,
        "tariff_price": round(float(tariff_price), 3),
        "optimizer_action": optimizer_action,
        "recommendation": recommendation,
    }


@app.post("/hems/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest) -> OptimizeResponse:
    schedule, total_cost = optimize_schedule(
        load_forecast=request.load_forecast,
        solar_forecast=request.solar_forecast,
        battery_capacity=request.battery_capacity,
        initial_soc=request.initial_soc,
        max_charge_rate=request.max_charge_rate,
        max_discharge_rate=request.max_discharge_rate,
        prices=request.prices,
    )

    return OptimizeResponse(schedule=schedule, total_cost=total_cost)


@app.post("/classify", response_model=ClassifyResponse)
def classify_scene(request: ClassifyRequest) -> ClassifyResponse:
    prediction = scene_classifier.predict(request.features.model_dump())
    return ClassifyResponse(**prediction)
