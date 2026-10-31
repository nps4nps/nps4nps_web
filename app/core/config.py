import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Set up centralized configuration

    Attributes:
        secret: secret key to sign HMAC
    """

    secret: str = "dev"

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


settings = Settings()
