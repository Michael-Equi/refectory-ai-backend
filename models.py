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
    section1: List[List[int]]
    section2: List[List[int]]
    section3: List[List[int]]
    homography: List[List[float]]
    homography_x: int
    homography_y: int
