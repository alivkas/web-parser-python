from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class Prices(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    cost: int


class PriceCreate(BaseModel):
    name: str
    cost: int