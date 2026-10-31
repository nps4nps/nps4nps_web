import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.log_config import setup_logger
from app.core.templates import configure_templates
from app.web.pages import debug, pages
from app.web.views import visualization

setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
configure_templates(app)

app.include_router(debug.router)
app.include_router(pages.router)
app.include_router(visualization.router)
