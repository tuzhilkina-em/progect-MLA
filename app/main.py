from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import random
from datetime import datetime, timedelta
from typing import List
import logging
from loguru import logger

from config import settings
from app.utils import CodeManager


def _configure_logging():
    logger.add("app.log", rotation="10 MB", level="INFO")


async def home():
    return RedirectResponse(url="/login")


async def welcome_page():
    return RedirectResponse(url="/login")


class FastAPIApp:
    def __init__(self):
        self.app = FastAPI()
        self.templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
        self.code_manager = CodeManager()
        self.security = HTTPBasic()
        self._setup_routes()
        _configure_logging()

    def _setup_routes(self):
        self.app.get("/")(home)
        self.app.get("/login", response_class=HTMLResponse)(self.login_page)
        self.app.post("/login", response_class=HTMLResponse)(self.handle_login)
        self.app.get("/welcome", response_class=HTMLResponse)(welcome_page)

        self.app.get("/admin", response_class=HTMLResponse)(self.admin_page)
        self.app.get("/admin/codes")(self.admin_codes)
        self.app.get("/admin/generate")(self.admin_generate)

    async def login_page(self, request: Request):
        return self.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "valid_codes": self.code_manager.get_all_codes(),
                "ttl_minutes": settings.CODE_TTL_MINUTES
            }
        )

    async def handle_login(self, request: Request, code: str = Form(...)):
        if not self.code_manager.is_valid_code(code):
            return self.templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "message": "Invalid or expired code",
                    "status": "error",
                    "valid_codes": self.code_manager.get_all_codes(),
                    "ttl_minutes": settings.CODE_TTL_MINUTES
                }
            )

        logger.info(f"User logged in with code: {code}")
        return self.templates.TemplateResponse(
            "welcome.html",
            {
                "request": request,
                "code": code
            }
        )

    def _verify_admin(self, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
        """Проверка логина и пароля администратора."""
        if (credentials.username != settings.ADMIN_USERNAME or
            credentials.password != settings.ADMIN_PASSWORD):
            logger.warning(f"Failed admin login attempt: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username

    def _admin_dependency(self):
        async def dep(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
            return self._verify_admin(credentials)

        return Depends(dep)

    def _setup_routes(self):
        self.app.get("/")(home)
        self.app.get("/login", response_class=HTMLResponse)(self.login_page)
        self.app.post("/login", response_class=HTMLResponse)(self.handle_login)
        self.app.get("/welcome", response_class=HTMLResponse)(welcome_page)

        # Защищенные маршруты (используют Depends)
        self.app.get("/admin", response_class=HTMLResponse)(self._create_admin_route(self.admin_page))
        self.app.get("/admin/codes")(self._create_admin_route(self.admin_codes))
        self.app.get("/admin/generate")(self._create_admin_route(self.admin_generate))

    def _create_admin_route(self, endpoint):
        """Обертка для маршрутов, требующих авторизации."""
        async def wrapper(request: Request = None, username: str = Depends(self._verify_admin)):
            return await endpoint(request) if request else await endpoint()
        return wrapper

    async def admin_page(self, request: Request):
        return self.templates.TemplateResponse(
            "admin.html",
            {"request": request, "username": "admin"}  # username можно получить из Depends
        )

    async def admin_codes(self, username: str = Depends(_admin_dependency)):
        return {"codes": self.code_manager.get_all_codes()}

    async def admin_generate(self, username: str = Depends(_admin_dependency)):
        new_code = self.code_manager.generate_code()
        logger.info(f"Admin generated new code: {new_code}")
        return {"status": "success", "code": new_code}



app_instance = FastAPIApp()
app = app_instance.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)