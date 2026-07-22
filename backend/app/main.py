"""FastAPI application entry point for the AI Resume Copilot backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.exceptions.handlers import generic_exception_handler, value_error_handler
from app.api.middleware.request_logging import RequestLoggingMiddleware
from app.api.routes import evaluation, health, resume, templates, upload
from app.config import get_settings
from app.utils.file_utils import ensure_dir
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-oriented AI Resume Copilot backend built on FastAPI + LangGraph.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

for directory in (
    settings.UPLOAD_DIR,
    settings.PARSED_DIR,
    settings.GENERATED_DIR,
    settings.EXPORT_DIR,
    settings.CACHE_DIR,
    settings.LOG_DIR,
):
    ensure_dir(directory)

ensure_dir("app/renderers/css")
app.mount("/static/css", StaticFiles(directory="app/renderers/css"), name="css")

app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(upload.router, prefix=settings.API_PREFIX)
app.include_router(resume.router, prefix=settings.API_PREFIX)
app.include_router(evaluation.router, prefix=settings.API_PREFIX)
app.include_router(templates.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def on_startup():
    logger.info("%s starting up (env=%s)", settings.APP_NAME, settings.APP_ENV)


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running.", "docs": "/docs"}
