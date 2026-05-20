from unittest.mock import Mock

from fastapi.testclient import TestClient

from app import main


def build_client() -> tuple[TestClient, Mock]:
    main.registry.reset()
    mqtt_mock = Mock()
    main.mqtt_client = mqtt_mock
    client = TestClient(main.app)
    return client, mqtt_mock


def test_health() -> None:
    client, _ = build_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_devices() -> None:
    client, _ = build_client()

    response = client.get("/devices")

    assert response.status_code == 200
    devices = response.json()

    assert len(devices) == 11
    assert {"solar_panel", "battery_soc", "grid_power"} <= set(devices)


def test_get_energy_summary() -> None:
    client, _ = build_client()
    main.registry.set_state("ceiling_light", 1.0)
    main.registry.set_state("thermostat", 22.0)
    main.registry.set_state("solar_panel", 1500.0)
    main.registry.set_state("battery_soc", 67.0)
    main.registry.set_state("grid_power", 560.0)

    response = client.get("/devices/energy")

    assert response.status_code == 200
    assert response.json() == {
        "total_load_kw": 2.06,
        "solar_kw": 1.5,
        "grid_kw": 0.56,
        "battery_soc_pct": 67.0,
        "by_device": {
            "ceiling_light": 0.06,
            "thermostat": 2.0,
        },
    }


def test_set_device_state() -> None:
    client, mqtt_mock = build_client()

    response = client.post("/devices/motion_hall/state", json={"value": 1.0})

    assert response.status_code == 200
    assert response.json()["state"] == 1.0
    mqtt_mock.publish_state.assert_called_once_with("motion_hall", 1.0)


def test_activate_scene_day() -> None:
    client, mqtt_mock = build_client()

    response = client.post("/scenes/day/activate")

    assert response.status_code == 200
    assert response.json()["scene"] == "day"
    assert response.json()["applied"]["ceiling_light"] == 1.0
    assert main.registry.get("ceiling_light")["state"] == 1.0
    mqtt_mock.publish_scene_confirmed.assert_called_once_with("day")


def test_invalid_scene_404() -> None:
    client, _ = build_client()

    response = client.post("/scenes/nonexistent/activate")

    assert response.status_code == 404
