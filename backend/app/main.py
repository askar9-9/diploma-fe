from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ML_SERVICE_URL
from app.ml_client import MLClient
from app.mqtt_handler import MQTTHandler
from app.routers.areas import router as areas_router
from app.routers.auth import router as auth_router
from app.routers.devices import router as devices_router
from app.routers.energy import router as energy_router
from app.routers.entities import router as entities_router
from app.routers.hems import router as hems_router
from app.routers.ml import router as ml_router
from app.routers.scenes import router as scenes_router
from app.routers.websocket import router as websocket_router
from app.websocket_manager import WebSocketManager
from app.db import engine
from db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(engine)
    app.state.mqtt_handler.start()
    try:
        yield
    finally:
        app.state.mqtt_handler.stop()


app = FastAPI(title="HomeIQ Backend API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.ws_manager = WebSocketManager()
app.state.ml_client = MLClient(ML_SERVICE_URL)
app.state.current_scene = None
app.state.last_confidence = None
app.state.last_decision_at = None
app.state.last_motion_at = None
app.state.mqtt_handler = MQTTHandler(app.state.ws_manager, app.state)
init_db(engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(areas_router)
app.include_router(devices_router)
app.include_router(entities_router)
app.include_router(energy_router)
app.include_router(hems_router)
app.include_router(ml_router)
app.include_router(scenes_router)
app.include_router(websocket_router)
