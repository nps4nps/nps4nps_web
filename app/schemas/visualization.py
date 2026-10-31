from pydantic import BaseModel


class DummyModel(BaseModel):
    sleepint: int = 30
