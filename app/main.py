import logging

from fastapi import FastAPI

from app.core.config import settings
from app.core.log_config import setup_logger
from app.web.pages import debug
from app.web.views import visualization

setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

app.include_router(debug.router)
app.include_router(visualization.router)
