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


class AlmanacInfo(BaseModel):
    date: str
    yi: List[str]
    ji: List[str]
    position_xi: str
    position_xi_desc: str
    position_fu: str
    position_fu_desc: str
    position_cai: str
    position_cai_desc: str
    sha_wei: str
    day_na_yin: str
    peng_zu_gan: str
    peng_zu_zhi: str


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
    is_holiday: Optional[bool] = None
    holiday_name: Optional[str] = None
    is_workday: Optional[bool] = None
    holiday_data_available: bool = True
