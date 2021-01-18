from pydantic import BaseModel
from typing import List


class Dish(BaseModel):
    contents: str
    image: str
    name: str
    round: bool
    section: int


class Stream(BaseModel):
    dishes: List[Dish]
