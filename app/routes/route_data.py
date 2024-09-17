from fastapi import APIRouter
from app.controllers.sensor_controller import SensorController

router = APIRouter()
sensor_controller = SensorController()

@router.get("/dados")
async def get_sensor_data():
    return sensor_controller.get_sensor_data()
