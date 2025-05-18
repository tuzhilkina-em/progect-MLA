from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import random
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "fXtn66xuno"
CODE_TTL_MINUTES = 3


app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


codes_db: List[Dict] = []


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def cleanup_expired_codes():
    global codes_db
    now = datetime.now()
    codes_db = [code for code in codes_db
                if now - code["created_at"] < timedelta(minutes=CODE_TTL_MINUTES)]


def get_valid_codes():
    cleanup_expired_codes()
    return [code["code"] for code in codes_db]


@app.get("/admin/codes")
async def admin_codes(_: str = Depends(verify_admin)):
    return {"codes": codes_db}


@app.get("/admin/generate")
async def admin_generate(_: str = Depends(verify_admin)):
    new_code = str(random.randint(10_000_000, 99_999_999))
    codes_db.append({
        "code": new_code,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=CODE_TTL_MINUTES)
    })
    return {"status": "success", "code": new_code}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "valid_codes": get_valid_codes(),
            "ttl_minutes": CODE_TTL_MINUTES
        }
    )


@app.post("/login", response_class=HTMLResponse)
async def handle_login(
        request: Request,
        code: str = Form(...)
):
    valid_codes = get_valid_codes()

    if code not in valid_codes:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "message": "Invalid or expired code",
                "status": "error",
                "valid_codes": valid_codes,
                "ttl_minutes": CODE_TTL_MINUTES
            }
        )

    return templates.TemplateResponse(
        "welcome.html",
        {
            "request": request,
            "code": code
        }
    )

@app.get("/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return RedirectResponse(url="/login")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)