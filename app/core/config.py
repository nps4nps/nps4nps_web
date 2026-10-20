from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Set up centralized configuration

    Attributes:
        secret: secret key to sign HMAC
    """

    secret: str = "dev"

    @model_validator(mode="after")
    def check_secret(self):
        if self.secret == "dev":
            raise RuntimeError("Error: Secret key not set")
        return self

    @property
    def repo_name(self) -> str:
        return "nps4nps/nps4nps_web"

    @property
    def app_name(self) -> str:
        return "NPs4NPs-Web"


settings = Settings()
