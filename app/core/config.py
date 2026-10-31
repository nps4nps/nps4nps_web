import logging
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Set up centralized configuration

    Attributes:
        secret: secret key to sign HMAC
    """

    secret: str = "dev"
    static_dir: Path = Field(default_factory=lambda: Path("/app/app/static"))

    @model_validator(mode="after")
    def check_secret(self):
        if self.secret == "dev":
            logger.error("Error: Secret key not set - do not use in production!")
        return self

    @property
    def repo_name(self) -> str:
        return "nps4nps/nps4nps_web"

    @property
    def app_name(self) -> str:
        return "NPs4NPs-Web"

    @property
    def broker_url(self) -> str:
        return "redis://redis:6379/0"

    @property
    def backend_url(self) -> str:
        return "redis://redis:6379/1"

    @property
    def task_time_limit(self) -> int:
        """Celery task time limit in seconds"""
        return 360

    @property
    def max_retries(self) -> int:
        """Celery task max retries"""
        return 3

    @property
    def celery_tasks_import(self) -> str:
        """Location to discover celery tasks"""
        return "app.services"


settings = Settings()
