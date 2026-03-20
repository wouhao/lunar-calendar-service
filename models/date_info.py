from typing import Optional, List
from pydantic import BaseModel


class LunarDate(BaseModel):
    year: int
    month: int
    day: int
    leap: bool
    label: str


class GanZhi(BaseModel):
    year: str
    month: str
    day: str


class DateInfo(BaseModel):
    solar: str
    lunar: LunarDate
    ganzhi: GanZhi
    zodiac: str
    constellation: str
    solar_term: Optional[str] = None
    festivals: List[str] = []
    weekday: int
    week_of_year: int
    is_holiday: bool
    holiday_name: Optional[str] = None
