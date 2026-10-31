import importlib.metadata

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from app.core.config import settings

templates = Jinja2Templates(directory=settings.static_dir.joinpath("templates"))


def configure_templates(app: FastAPI):
    """Configure globals in template"""
    templates.env.globals["openapi_url"] = app.docs_url
    templates.env.globals["redoc_url"] = app.redoc_url
    templates.env.globals["version_app"] = importlib.metadata.version("nps4nps-web")
