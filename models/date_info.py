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


class AdvancedInfo(BaseModel):
    date: str                          # 输入日期回显

    # 八字四柱
    ba_zi: List[str]                   # getBaZi() 四柱，以立春换年
    ba_zi_wu_xing: List[str]           # getBaZiWuXing() 四柱五行
    year_gan_zhi: str                  # getYearInGanZhi() 以正月初一换年
    month_gan_zhi: str                 # getMonthInGanZhi()
    day_gan_zhi: str                   # getDayInGanZhi()
    day_gan: str                       # 日主天干
    day_zhi: str                       # 日主地支

    # 纳音五行
    year_na_yin: str                   # getYearNaYin()
    month_na_yin: str                  # getMonthNaYin()
    day_na_yin: str                    # getDayNaYin()
    time_na_yin: str                   # getTimeNaYin()

    # 二十八宿
    xiu: str                           # getXiu()
    xiu_luck: str                      # getXiuLuck()
    xiu_song: str                      # getXiuSong()

    # 胎神
    day_position_tai: str              # getDayPositionTai()
    month_position_tai: Optional[str]  # getMonthPositionTai()，可能为空

    # 黄道/黑道十二神
    tian_shen: str                     # getDayTianShen()
    tian_shen_luck: str                # getDayTianShenLuck()
    tian_shen_type: str                # getDayTianShenType()，黄道/黑道

    # 佛历/道历
    foto: Optional[str] = None        # getFoto() 佛历日期字符串
    tao: Optional[str] = None         # getTao() 道历日期字符串


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
