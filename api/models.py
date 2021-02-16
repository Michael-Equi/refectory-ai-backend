from pydantic import BaseModel
from typing import List


class Dish(BaseModel):
    contents: str
    name: str
    round: bool
    section: int


class Stream(BaseModel):
    dishes: List[Dish]


class Calibration(BaseModel):
    roi_top_left: List[int]
    roi_bottom_right: List[int]
    homography: List[List[float]]
    homography_x: int
    homography_y: int
