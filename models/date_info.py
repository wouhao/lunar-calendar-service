"""
Pydantic models for the get_date_info response schema.
"""
from typing import List, Optional

from pydantic import BaseModel


class LunarDate(BaseModel):
    """农历日期"""

    year: int
    month: int
    day: int
    leap: bool
    label: str  # 如"正月初一"


class GanZhi(BaseModel):
    """干支纪年/月/日"""

    year: str  # 如"甲辰"
    month: str
    day: str


class DateInfo(BaseModel):
    """get_date_info 返回结构"""

    solar: str  # YYYY-MM-DD
    lunar: LunarDate
    ganzhi: GanZhi
    zodiac: str  # 生肖，如"龙"
    constellation: str  # 星座，如"水瓶座"
    solar_term: Optional[str]  # 节气，无则 None
    festivals: List[str]  # 节日列表
    weekday: int  # 1-7，1=周一
    week_of_year: int
    is_holiday: bool
    holiday_name: Optional[str]  # 法定节假日名称
