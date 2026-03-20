"""
date_service.py — 核心日期信息服务

实现 get_date_info(date: str) -> DateInfo
提供共享 helper functions 供 P1-2~P1-6 复用
"""

import json
import sys
from pathlib import Path
from datetime import date as dt_date, datetime
from typing import Optional, List

from lunar_python import Solar, Lunar

# 确保 models 包可以被导入
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from models.date_info import DateInfo, LunarDate, GanZhi

# holidays JSON 路径
_DATA_DIR = _ROOT / "data"
_HOLIDAYS_CACHE: dict[int, dict] = {}


# ─────────────────────────────────────────
# Helper: 加载节假日数据
# ─────────────────────────────────────────

def _load_holidays(year: int) -> dict:
    """加载指定年份节假日 JSON，缓存避免重复 IO。"""
    if year in _HOLIDAYS_CACHE:
        return _HOLIDAYS_CACHE[year]

    path = _DATA_DIR / f"holidays_{year}.json"
    if not path.exists():
        raise ValueError(f"No holiday data for year {year}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    _HOLIDAYS_CACHE[year] = data
    return data


def _get_holiday_info(date_str: str) -> tuple[bool, Optional[str], bool]:
    """
    查询某日期的节假日信息。
    返回 (is_holiday, holiday_name, is_workday)
    - type=holiday → is_holiday=True, is_workday=False
    - type=workday → is_holiday=False, is_workday=True
    - 不在列表 → is_holiday=False, is_workday=False（需调用方判断是否工作日）
    """
    year = int(date_str[:4])
    try:
        data = _load_holidays(year)
    except ValueError:
        raise

    for entry in data.get("holidays", []):
        if entry["date"] == date_str:
            etype = entry["type"]
            name = entry["name"]
            if etype == "holiday":
                return True, name, False
            elif etype == "workday":
                return False, None, True
    # 不在列表中
    return False, None, False


# ─────────────────────────────────────────
# Helper: 农历 label
# ─────────────────────────────────────────

def _build_lunar_label(lunar: Lunar) -> str:
    """构造农历 label，如 '正月初一'、'（闰）四月初一'"""
    month_cn = lunar.getMonthInChinese()
    day_cn = lunar.getDayInChinese()
    leap = lunar.getMonth() < 0
    prefix = "（闰）" if leap else ""
    return f"{prefix}{month_cn}月{day_cn}"


# ─────────────────────────────────────────
# Helper: 节气
# ─────────────────────────────────────────

def _get_solar_term(y: int, m: int, d: int) -> Optional[str]:
    """返回当天节气中文名，若无则返回 None。"""
    solar = Solar.fromYmd(y, m, d)
    lunar = solar.getLunar()
    jq = lunar.getJieQi()
    return jq if jq else None


# ─────────────────────────────────────────
# Helper: 节日列表
# ─────────────────────────────────────────

_SOLAR_FESTIVALS: list[tuple[int, int, str]] = [
    (1, 1, "元旦"),
    (2, 14, "情人节"),
    (3, 8, "妇女节"),
    (3, 12, "植树节"),
    (4, 1, "愚人节"),
    (5, 1, "劳动节"),
    (5, 4, "青年节"),
    (6, 1, "儿童节"),
    (7, 1, "建党节"),
    (8, 1, "建军节"),
    (9, 9, "重阳节（阳历）"),  # 重阳是农历，这里只是占位
    (9, 10, "教师节"),
    (10, 1, "国庆节"),
    (10, 31, "万圣节"),
    (11, 11, "光棍节"),
    (12, 24, "平安夜"),
    (12, 25, "圣诞节"),
]

_LUNAR_FESTIVALS: list[tuple[int, int, str]] = [
    (1, 1, "春节"),
    (1, 15, "元宵节"),
    (5, 5, "端午节"),
    (7, 7, "七夕节"),
    (7, 15, "中元节"),
    (8, 15, "中秋节"),
    (9, 9, "重阳节"),
    (12, 8, "腊八节"),
    (12, 23, "小年"),  # 北方
    (12, 30, "除夕"),  # 大月
    (12, 29, "除夕"),  # 小月（近似）
]


def _get_festivals(solar: Solar, lunar: Lunar) -> List[str]:
    """获取当天节日列表（阳历节日 + 农历节日）。"""
    festivals: List[str] = []

    sm, sd = solar.getMonth(), solar.getDay()
    for fmonth, fday, fname in _SOLAR_FESTIVALS:
        if sm == fmonth and sd == fday:
            festivals.append(fname)

    lm, ld = abs(lunar.getMonth()), lunar.getDay()
    for fmonth, fday, fname in _LUNAR_FESTIVALS:
        if lm == fmonth and ld == fday:
            # 避免重复（如劳动节既是阳历又可能与农历重合）
            if fname not in festivals:
                festivals.append(fname)

    return festivals


# ─────────────────────────────────────────
# 主接口
# ─────────────────────────────────────────

def is_holiday(date: str) -> dict:
    """
    查询某天是否放假或调休上班。

    Args:
        date: 日期字符串，格式 YYYY-MM-DD

    Returns:
        dict，包含:
          - date: 查询日期
          - is_holiday: 是否放假（type=holiday）
          - is_workday: 是否调休上班（type=workday）
          - holiday_name: 节假日名称（放假时有值，调休/普通日为 null）
          - note: 说明，"放假" / "调休上班" / "普通工作日" / "普通周末"

    Raises:
        ValueError: 日期格式错误或缺少节假日数据（年份不在 data/ 目录中）
    """
    # 验证日期格式
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，收到: {date!r}")

    holiday_flag, holiday_name, workday_flag = _get_holiday_info(date)

    if holiday_flag:
        note = "放假"
    elif workday_flag:
        note = "调休上班"
    else:
        # 普通日 — 按星期判断
        weekday = d.isoweekday()  # 1=周一…7=周日
        note = "普通周末" if weekday >= 6 else "普通工作日"

    return {
        "date": date,
        "is_holiday": holiday_flag,
        "is_workday": workday_flag,
        "holiday_name": holiday_name,
        "note": note,
    }


def get_date_info(date: str) -> DateInfo:
    """
    获取指定日期的完整信息。

    Args:
        date: 日期字符串，格式 YYYY-MM-DD

    Returns:
        DateInfo 对象，包含阳历/阴历/干支/生肖/星座/节气/节日/节假日等信息

    Raises:
        ValueError: 日期格式错误或缺少节假日数据
    """
    # 解析日期
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，收到: {date!r}")

    y, m, day = d.year, d.month, d.day

    # lunar-python 对象
    solar = Solar.fromYmd(y, m, day)
    lunar = solar.getLunar()

    # 农历信息
    # getMonth() 返回负数表示闰月
    lunar_month_raw = lunar.getMonth()
    lunar_is_leap = lunar_month_raw < 0
    lunar_date = LunarDate(
        year=lunar.getYear(),
        month=abs(lunar_month_raw),
        day=lunar.getDay(),
        leap=lunar_is_leap,
        label=_build_lunar_label(lunar),
    )

    # 干支
    ganzhi = GanZhi(
        year=lunar.getYearInGanZhi(),
        month=lunar.getMonthInGanZhi(),
        day=lunar.getDayInGanZhi(),
    )

    # 生肖（用年干支对应的生肖）
    zodiac = lunar.getYearShengXiao()

    # 星座（library 返回如"水瓶"，补"座"变成"水瓶座"）
    constellation = solar.getXingZuo() + "座"

    # 节气
    solar_term = _get_solar_term(y, m, day)

    # 节日
    festivals = _get_festivals(solar, lunar)

    # 周几（1=周一...7=周日）
    weekday = d.isoweekday()

    # 第几周
    week_of_year = d.isocalendar()[1]

    # 节假日
    is_holiday, holiday_name, is_workday = _get_holiday_info(date)

    return DateInfo(
        solar=date,
        lunar=lunar_date,
        ganzhi=ganzhi,
        zodiac=zodiac,
        constellation=constellation,
        solar_term=solar_term,
        festivals=festivals,
        weekday=weekday,
        week_of_year=week_of_year,
        is_holiday=is_holiday,
        holiday_name=holiday_name,
        is_workday=is_workday,
    )


# ─────────────────────────────────────────
# 农历 → 公历转换
# ─────────────────────────────────────────

def lunar_to_solar(year: int, month: int, day: int, leap_month: bool = False) -> str:
    """
    将农历日期转换为公历日期字符串。

    Args:
        year: 农历年份
        month: 农历月份（1-12）
        day: 农历日（1-30）
        leap_month: 是否为闰月，默认 False

    Returns:
        公历日期字符串，格式 YYYY-MM-DD

    Raises:
        ValueError: 农历日期无效
    """
    # 闰月用负数月份表示
    lunar_month = -month if leap_month else month
    lunar = Lunar.fromYmd(year, lunar_month, day)
    solar = lunar.getSolar()
    return f"{solar.getYear():04d}-{solar.getMonth():02d}-{solar.getDay():02d}"
