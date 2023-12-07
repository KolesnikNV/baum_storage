from datetime import datetime
from typing import List

from pydantic import BaseModel


class Message(BaseModel):
    title: str


class ResultData(BaseModel):
    datetime: str
    title: str
    text: str
    x_avg_count_in_line: int


class ResultList(BaseModel):
    data: List[ResultData]
