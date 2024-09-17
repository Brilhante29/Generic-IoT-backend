from fastapi import APIRouter
from app.routes import route_led_control, route_sensor, route_page

api_router = APIRouter()

# Inclui as rotas relacionadas ao LED
api_router.include_router(route_led_control.router, prefix="/led", tags=["LED Control"])

# Inclui as rotas relacionadas aos dados dos sensores
api_router.include_router(route_sensor.router, prefix="/sensor", tags=["Sensor Data"])

# Inclui a rota para a página principal
api_router.include_router(route_page.router, tags=["Main Page"])
