from fastapi import APIRouter
from app.controllers.led_controller import LEDController

router = APIRouter()
led_controller = LEDController()

@router.get("/led/{state}")
async def control_led(state: str):
    return led_controller.control_led(state)
