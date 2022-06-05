import secrets, os
from deta import Deta
# from deta import app as app_cron
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv(override=True)
__version__ = "0.0.1"
PROJECT_KEY = os.environ.get("PROJECT_KEY", "")

app = FastAPI(version=__version__, docs_url=False, redoc_url=False)
deta = Deta(PROJECT_KEY)
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()
users_db = deta.Base("users")


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_http_exception_handler(request, exc):
    return RedirectResponse("/")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/register")
async def set_register(request: Request):
    return RedirectResponse("/", status.HTTP_302_FOUND)


@app.post("/login")
async def set_login(request: Request):
    return RedirectResponse("/", status.HTTP_302_FOUND)


@app.post("/protocol")
async def set_protocol(credentials: HTTPBasicCredentials = Depends(security)):
    user = {"username": credentials.username, "password": credentials.password}
    return RedirectResponse("/", status.HTTP_302_FOUND)


@app.post("/unsubscribe/{email}")
async def unsubscribe(request: Request, email: str = None):
    # TODO remove email 
    return RedirectResponse("/", status.HTTP_302_FOUND)


# @app_cron.lib.cron()
# def cron_job(event):

#     file = drive.get(name)
#     # TODO cron para verificar arquivos com determinado ID e enviar email notificando

#     deta.send_email(to, subject, message)

#     return "verifica arquivo recente e busca"
