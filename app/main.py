from fastapi import FastAPI
from app.routes.router import api_router
import threading
from app.services.mqtt_service import MQTTService

app = FastAPI()

mqtt_service = MQTTService()

# Iniciando o MQTT em uma thread separada
mqtt_thread = threading.Thread(target=mqtt_service.start)
mqtt_thread.daemon = True
mqtt_thread.start()

# Registrando as rotas
app.include_router(api_router)
