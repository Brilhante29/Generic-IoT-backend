from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.controllers.page_controller import PageController

router = APIRouter()
page_controller = PageController()

@router.get("/", response_class=HTMLResponse)
async def control_page(request: Request):
    return page_controller.control_page(request)
