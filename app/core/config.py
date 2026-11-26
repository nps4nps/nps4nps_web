import logging
import pathlib
import re
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
        return 240

    @property
    def max_retries(self) -> int:
        """Celery task max retries"""
        return 3

    @property
    def celery_tasks_import(self) -> list[str]:
        """Location to discover celery tasks"""
        return ["app.tasks.add", "app.tasks.sampling"]

    @property
    def nanopublication_endpoint(self) -> str:
        """URL to send SPARQL query to"""
        return "https://query.knowledgepixels.com/repo/full"

    @property
    def request_timeout(self) -> int:
        """Max time in seconds to wait for an API call"""
        return 10

    @property
    def coordinates_re(self) -> re.Pattern:
        """ISO 6709 style coordinates, e.g. +46.575707+14.395198+740"""
        return re.compile(
            r"^([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)?/?$"
        )

    @property
    def time_update_defaults(self) -> int:
        """Time in seconds to update maps from live sources"""
        return 1800

    @property
    def map_dir(self) -> pathlib.Path:
        """Location of stored default maps"""
        return Path("/data/maps")

    @property
    def dflt_sample_map_name(self) -> str:
        """Name of stored default sample map"""
        return "defaultSampleMap"


settings = Settings()
