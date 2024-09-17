from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

class PageController:
  def control_page(self, request: Request):
    return templates.TemplateResponse("control_page.html", {"request": request})
