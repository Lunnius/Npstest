from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("Index.html", {"request": request})

@router.get("/termo", response_class=HTMLResponse)
def termo(request: Request):
    return templates.TemplateResponse("TermoAceite.html", {"request": request})


@router.get("/ressalvas", response_class=HTMLResponse)
def ressalvas(request: Request):
    return templates.TemplateResponse("Ressalvas.html", {"request": request})


@router.get("/nps", response_class=HTMLResponse)
def nps(request: Request):
    return templates.TemplateResponse("NPS2System.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/user", response_class=HTMLResponse)
def user(request: Request):
    return templates.TemplateResponse("User.html", {"request": request})

@router.get("/nps-motor", response_class=HTMLResponse)
def nps_motor(request: Request):
    return templates.TemplateResponse("NPSMotor.html", {"request": request})

@router.get("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools():
    return {}

