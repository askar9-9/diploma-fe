from app.forecasters import LSTMForecaster, predict_solar


def test_predict_load_returns_24_hours_with_fallback():
    forecaster = LSTMForecaster(
        model_path="missing_model.keras",
        scaler_path="missing_scaler.pkl",
    )
    result = forecaster.predict_load([1.0] * 168)

    assert len(result) == 24
    assert all(isinstance(x, float) for x in result)
    assert all(x >= 0.0 for x in result)


def test_predict_solar_zero_at_night():
    result = predict_solar(hour=0, month=7)

    assert len(result) == 24
    assert result[0] == 0.0
    assert result[2] == 0.0
    assert result[23] == 0.0


def test_predict_solar_positive_in_daytime():
    result = predict_solar(hour=0, month=7)

    assert len(result) == 24
    assert result[12] > 0.0


def test_predict_solar_has_lower_winter_generation():
    summer = predict_solar(hour=12, month=7)
    winter = predict_solar(hour=12, month=1)

    assert winter[0] < summer[0]
