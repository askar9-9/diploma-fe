import os


MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
DEVICE_SIMULATOR_URL = os.getenv("DEVICE_SIMULATOR_URL", "http://localhost:8002")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/homeiq.db")
JWT_SECRET = os.getenv("JWT_SECRET", "homeiq-secret-2026")
ML_CONFIDENCE_THRESHOLD = float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.7"))
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "homeiq2026"
