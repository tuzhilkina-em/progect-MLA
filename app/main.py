from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json

from app.utils import add_to_json, get_last_code
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

def generate_code() -> str:
    return str(random.randint(10_000_000, 99_999_999))


@app.get("/generate")
async def generate_page():
    new_code = generate_code()
    logger.info(f"Generated code: {new_code}")

    add_to_json(new_code)
    last_code = get_last_code()

    if new_code == last_code:
        logger.info("Codes match! Returning welcome message")
        return {
            "status": "success",
            "message": "welcome to hell",
            "code": new_code,
            "match": True
        }

    return {
        "status": "success",
        "message": "new code generated",
        "code": new_code,
        "match": False
    }


@app.get("/")
def home():
    return {"message": "welcome to hell"}


@app.get("/codes")
def list_codes():
    from app.utils import get_json_path
    try:
        return json.loads(get_json_path().read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


@app.post("/generate")
async def generate_from_form(
        code: str = Form(...)
):
    last_code = get_last_code()
    if code != last_code:
        return {"status": "error", "message": "Invalid code!"}

    add_to_json(code)

    response_data = {
        "status": "success",
        "code": code,
        "match": code == last_code,
        "source": "form",
        "message": "welcome to hell"
    }

    return response_data


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def handle_login(
        request: Request,
        code: str = Form(...)
):

    message = "Data received successfully!"
    status = "success"

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": message,
            "status": status,
        }
    )