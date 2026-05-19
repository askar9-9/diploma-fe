from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import ML_SERVICE_URL
from backend.app.db import engine
from backend.app.ml_client import MLClient
from backend.app.mqtt_handler import MQTTHandler
from backend.app.routers.auth import router as auth_router
from backend.app.routers.devices import router as devices_router
from backend.app.routers.scenarios import router as scenarios_router
from backend.app.routers.simulation import router as simulation_router
from backend.app.routers.websocket import router as websocket_router
from backend.app.websocket_manager import WebSocketManager
from backend.db.init_db import init_db


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
init_db(engine)
app.state.ws_manager = WebSocketManager()
app.state.ml_client = MLClient(ML_SERVICE_URL)
app.state.mqtt_handler = MQTTHandler(app.state.ws_manager, app.state.ml_client)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(devices_router)
app.include_router(scenarios_router)
app.include_router(simulation_router)
app.include_router(websocket_router)
