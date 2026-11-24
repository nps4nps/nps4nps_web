from pydantic import BaseModel, Field


# TODO: remove this model
class AddModel(BaseModel):
    x: int = Field(...)
    y: int = Field(...)
