import secrets, os
from deta import Deta

# from deta import app as app_cron
from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Depends,
    Request,
    Response,
    Form,
    Cookie,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from passlib.context import CryptContext
from typing import Optional, Union
from datetime import datetime, timedelta
from jose import jwt


__version__ = "0.0.1"
load_dotenv(override=True)
PROJECT_KEY = os.environ.get("PROJECT_KEY", "")

app = FastAPI(version=__version__, docs_url=False, redoc_url=False)
deta = Deta(PROJECT_KEY)
templates = Jinja2Templates(directory="templates")
users_db = deta.Base("users")
protocols_db = deta.Base("protocols")


ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def get_user(email: str):
    user = users_db.get(email)
    return user


def authenticate_user(email: str, password: str):
    try:
        user = get_user(email)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
    if not user:
        return False
    if not verify_password(password, user.get("password")):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, PROJECT_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_or_none(
    access_token: Union[str, None] = Cookie(default=None)
):
    try:
        if access_token is None:
            return None
        payload = jwt.decode(access_token, PROJECT_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except Exception as e:
        return None
    user = get_user(email)
    if user is None:
        return None
    return user


async def get_current_user(access_token: Union[str, None] = Cookie(default=None)):
    """Get logged user or raises HTTP 401"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = await get_current_user_or_none(access_token)
    if user is None:
        raise credentials_exception
    return user


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_http_exception_handler_404(request, exc):
    return RedirectResponse("/")


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def custom_http_exception_handler_401(request, exc):
    return RedirectResponse("/?error=login", status.HTTP_302_FOUND)


@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
async def custom_http_exception_handler_422(request, exc):
    return RedirectResponse("/?error=unprocessable", status.HTTP_302_FOUND)


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, error: str = None, user: dict = Depends(get_current_user_or_none)
):
    context = {"request": request, "error": error, "user": user}
    return templates.TemplateResponse("index.html", context)


@app.post("/register")
async def set_register(email: str = Form(...), password: str = Form(...)):
    url = "/"
    user = users_db.get(email)
    if user is None:
        new_user = {
            "password": get_password_hash(password),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "protocols": [],
        }
        users_db.put(new_user, email)
    else:
        url += "?error=register"
    return RedirectResponse(url, status.HTTP_302_FOUND)


@app.post("/login")
async def set_login(email: str = Form(...), password: str = Form(...)):
    response = RedirectResponse("/", status.HTTP_302_FOUND)
    user = authenticate_user(email, password)
    if not user:
        return RedirectResponse("/?error=login", status.HTTP_302_FOUND)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["key"]}, expires_delta=access_token_expires
    )
    response.set_cookie("access_token", access_token)
    return response


@app.post("/protocol")
async def set_protocol(
    protocol: str = Form(...), user: dict = Depends(get_current_user)
):
    protocols = user.get("protocols", [])
    if not protocol in [i["id"] for i in protocols]:
        protocols.append(
            {
                "status_ok": False,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "updated_at": None,
                "id": protocol,
            }
        )
        user["protocols"] = protocols
        users_db.put(user, user["key"])
    else:
        print("protocol already exists")
    return RedirectResponse("/", status.HTTP_302_FOUND)


@app.get("/delete/protocol/{protocol}")
async def delete_protocol(protocol: str, user: dict = Depends(get_current_user)):
    protocols = user.get("protocols", [])
    protocols = [i for i in protocols if i["id"] != protocol]
    user["protocols"] = protocols
    users_db.put(user, user["key"])
    return RedirectResponse("/", status.HTTP_302_FOUND)


# @app_cron.lib.cron()
# def cron_job(event):

#     file = drive.get(name)
#     # TODO cron para verificar arquivos com determinado ID e enviar email notificando

#     deta.send_email(to, subject, message)

#     return "verifica arquivo recente e busca"
