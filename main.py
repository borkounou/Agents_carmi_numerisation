from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from routers.admin import router
import os
from fastapi.templating import Jinja2Templates
from config.config import https_url_for

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError


# import secrets
# # Generate a random 256-bit key encoded as a hexadecimal string
# secret_key = secrets.token_hex(32)  # 32 bytes = 256 bits
# print("Generated JWT Secret Key:", secret_key)


app = FastAPI()

app.mount("/static", StaticFiles(directory='./static'), name="static")
app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")
app.mount("/profiles", StaticFiles(directory="profiles"), name="profiles")

app.include_router(router)


templates = Jinja2Templates(directory="templates")
templates.env.globals["https_url_for"] = https_url_for



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request:Request, exc:StarletteHTTPException):
    template_name = f"{exc.status_code}.html"
    return templates.TemplateResponse(template_name, {"request": request, "message": exc.detail,"body_class": ""}, status_code=exc.status_code)



# Handle generic 500 errors
@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("500.html", {"request": request, "message": "An internal error occurred. Please try again later.", "body_class": ""}, status_code=500)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid input: Ensure the correct data type is provided.",
            "errors": exc.errors(),
        },
    )
