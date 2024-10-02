from typing import Optional
from typing_extensions import Annotated

from pydantic import BaseModel, Field, AfterValidator

MyStr = Annotated[str, AfterValidator(lambda x: x.lower())]


class Message(BaseModel):
    message: str


class Breed(BaseModel):
    name: MyStr = Field(max_length=100)


class CatShortBase(BaseModel):
    color: MyStr = Field(..., max_length=30)
    age: int = Field(..., ge=0, lt=300)


class CatBase(BaseModel):
    description: MyStr = Field(..., max_length=150)
    breed: Breed


class CatShort(CatShortBase):
    id: int


class CatIn(CatShortBase, CatBase):
    pass


class CatOut(CatShort, CatBase):
    pass


class UpdateCat(BaseModel):
    color: Optional[MyStr] = Field(None, max_length=30)
    age: Optional[int] = Field(None, ge=0, lt=300)
    breed: Optional[Breed] = None
    description: Optional[MyStr] = Field(None, max_length=100)
