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


class Calibration(BaseModel):
    homography: List[List[float]]
    homography_x: int
    homography_y: int
