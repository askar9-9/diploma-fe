from fastapi import APIRouter, Depends, Request

from backend.app.auth import get_current_user


router = APIRouter(
    prefix="/simulation",
    tags=["simulation"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/start")
def start_simulation(request: Request) -> dict[str, object]:
    request.app.state.mqtt_handler.publish_simulation_control("start", speed=30)
    return {"status": "queued", "action": "start", "speed": 30}


@router.post("/stop")
def stop_simulation(request: Request) -> dict[str, str]:
    request.app.state.mqtt_handler.publish_simulation_control("stop")
    return {"status": "queued", "action": "stop"}


@router.post("/reset")
def reset_simulation(request: Request) -> dict[str, str]:
    request.app.state.mqtt_handler.publish_simulation_control("reset")
    return {"status": "queued", "action": "reset"}
