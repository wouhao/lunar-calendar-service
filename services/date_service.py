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

from models.date_info import DateInfo, LunarDate, GanZhi, AlmanacInfo, AdvancedInfo

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


def _get_holiday_info(date_str: str) -> tuple[Optional[bool], Optional[str], Optional[bool], bool]:
    """
    查询某日期的节假日信息。
    返回 (is_holiday, holiday_name, is_workday, data_available)
    - type=holiday → is_holiday=True, is_workday=False, data_available=True
    - type=workday → is_holiday=False, is_workday=True, data_available=True
    - 不在列表 → is_holiday=False, is_workday=False, data_available=True
    - 无数据 → is_holiday=None, is_workday=None, data_available=False
    """
    year = int(date_str[:4])
    try:
        data = _load_holidays(year)
    except ValueError:
        # 该年份节假日数据不存在，返回 None 表示无法判断
        return None, None, None, False

    for entry in data.get("holidays", []):
        if entry["date"] == date_str:
            etype = entry["type"]
            name = entry["name"]
            if etype == "holiday":
                return True, name, False, True
            elif etype == "workday":
                return False, None, True, True
    # 不在列表中
    return False, None, False, True


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
]


def _is_chuxi(lunar: Lunar) -> bool:
    """判断当天是否是除夕（腊月最后一天）。"""
    lm = abs(lunar.getMonth())
    ld = lunar.getDay()
    if lm != 12:
        return False
    # 获取腊月下一天的农历月份：若变为正月（1），则今天是腊月最后一天
    solar = lunar.getSolar()
    from datetime import timedelta
    from datetime import date as _date
    next_day = _date(solar.getYear(), solar.getMonth(), solar.getDay()) + timedelta(days=1)
    next_solar = Solar.fromYmd(next_day.year, next_day.month, next_day.day)
    next_lunar = next_solar.getLunar()
    next_lm = abs(next_lunar.getMonth())
    return next_lm == 1


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

    # 除夕：腊月最后一天（腊月29或30，按该年腊月实际天数判断）
    if _is_chuxi(lunar) and "除夕" not in festivals:
        festivals.append("除夕")

    return festivals


# ─────────────────────────────────────────
# 节假日列表接口
# ─────────────────────────────────────────

def get_holidays(year: int) -> dict:
    """
    获取指定年份的全年节假日列表。

    Args:
        year: 年份，如 2025

    Returns:
        dict，格式：
        {
            "year": 2025,
            "holidays": [
                {"date": "2025-01-01", "name": "元旦", "type": "holiday|workday"},
                ...
            ],
            "total_holidays": N,   # type=holiday 的条目数
            "total_workdays": N    # type=workday（调休补班）的条目数
        }

    Raises:
        ValueError: 缺少该年份节假日数据
    """
    data = _load_holidays(year)  # 缺失年份会抛出 ValueError

    holidays_list = data.get("holidays", [])
    total_holidays = sum(1 for h in holidays_list if h.get("type") == "holiday")
    total_workdays = sum(1 for h in holidays_list if h.get("type") == "workday")

    return {
        "year": year,
        "holidays": [
            {"date": h["date"], "name": h["name"], "type": h["type"]}
            for h in holidays_list
        ],
        "total_holidays": total_holidays,
        "total_workdays": total_workdays,
    }


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
          - is_holiday: 是否放假（type=holiday），无数据时为 None
          - is_workday: 是否调休上班（type=workday），无数据时为 None
          - holiday_name: 节假日名称（放假时有值，调休/普通日为 null）
          - note: 说明，"放假" / "调休上班" / "普通工作日" / "普通周末"
          - error: 当该年份节假日数据不存在时，包含此字段

    Raises:
        ValueError: 日期格式错误
    """
    # 验证日期格式
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，收到: {date!r}")

    year = int(date[:4])
    holiday_flag, holiday_name, workday_flag, data_available = _get_holiday_info(date)

    if not data_available:
        return {
            "date": date,
            "is_holiday": None,
            "is_workday": None,
            "holiday_name": None,
            "note": None,
            "error": f"No holiday data for year {year}",
        }

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

    if d.year < 1900 or d.year > 2100:
        raise ValueError("Year must be between 1900 and 2100")

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
    is_holiday_flag, holiday_name, is_workday_flag, data_available = _get_holiday_info(date)

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
        is_holiday=is_holiday_flag,
        holiday_name=holiday_name,
        is_workday=is_workday_flag,
        holiday_data_available=data_available,
    )


# ─────────────────────────────────────────
# 全年 24 节气
# ─────────────────────────────────────────

def get_solar_terms(year: int) -> list[dict]:
    """
    获取指定年份的全部 24 节气。

    Args:
        year: 公历年份，如 2025

    Returns:
        list of dict，每项 {"date": "YYYY-MM-DD", "name": "节气中文名"}
        按日期升序排列，共 24 条
    """
    # 以该年农历正月初一为锚点，取节气表
    anchor = Lunar.fromYmd(year, 1, 1)
    table = anchor.getJieQiTable()  # dict: name -> Solar

    result: list[dict] = []
    for solar in table.values():
        # 只保留公历年份等于 year 的节气
        if solar.getYear() != year:
            continue
        name = solar.getLunar().getJieQi()
        if not name:
            continue
        date_str = f"{solar.getYear():04d}-{solar.getMonth():02d}-{solar.getDay():02d}"
        result.append({"date": date_str, "name": name})

    # 按日期升序排序
    result.sort(key=lambda x: x["date"])
    return result


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


# ─────────────────────────────────────────
# 黄历 / 宜忌接口
# ─────────────────────────────────────────

def get_almanac(date: str) -> AlmanacInfo:
    """
    获取指定日期的黄历信息（宜忌、吉神方位、纳音、彭祖百忌等）。

    Args:
        date: 日期字符串，格式 YYYY-MM-DD

    Returns:
        AlmanacInfo 对象

    Raises:
        ValueError: 日期格式错误
    """
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，收到: {date!r}")

    if d.year < 1900 or d.year > 2100:
        raise ValueError("Year must be between 1900 and 2100")

    y, m, day = d.year, d.month, d.day
    lunar = Solar.fromYmd(y, m, day).getLunar()

    return AlmanacInfo(
        date=date,
        yi=lunar.getDayYi(),
        ji=lunar.getDayJi(),
        position_xi=lunar.getDayPositionXi(),
        position_xi_desc=lunar.getDayPositionXiDesc(),
        position_fu=lunar.getDayPositionFu(),
        position_fu_desc=lunar.getDayPositionFuDesc(),
        position_cai=lunar.getDayPositionCai(),
        position_cai_desc=lunar.getDayPositionCaiDesc(),
        sha_wei=lunar.getSha(),
        day_na_yin=lunar.getDayNaYin(),
        peng_zu_gan=lunar.getPengZuGan(),
        peng_zu_zhi=lunar.getPengZuZhi(),
    )


# ─────────────────────────────────────────
# 公历 → 农历转换
# ─────────────────────────────────────────

def solar_to_lunar(date: str) -> LunarDate:
    """
    将公历日期转换为农历 LunarDate。

    Args:
        date: 公历日期字符串，格式 YYYY-MM-DD

    Returns:
        LunarDate 对象，包含农历年月日、是否闰月及中文 label

    Raises:
        ValueError: 日期格式错误
    """
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，收到: {date!r}")

    if d.year < 1900 or d.year > 2100:
        raise ValueError("Year must be between 1900 and 2100")

    solar = Solar.fromYmd(d.year, d.month, d.day)
    lunar = solar.getLunar()

    lunar_month_raw = lunar.getMonth()
    lunar_is_leap = lunar_month_raw < 0

    return LunarDate(
        year=lunar.getYear(),
        month=abs(lunar_month_raw),
        day=lunar.getDay(),
        leap=lunar_is_leap,
        label=_build_lunar_label(lunar),
    )


# ─────────────────────────────────────────
# Phase 3：高级信息接口
# ─────────────────────────────────────────

def get_advanced_info(date: str, hour: int = 12) -> AdvancedInfo:
    """
    获取指定日期的高级命理信息。

    Args:
        date: 日期字符串，格式 YYYY-MM-DD
        hour: 时辰对应小时（0-23），用于八字时柱计算，默认 12（午时）

    Returns:
        AdvancedInfo 对象，包含八字四柱、五行、二十八宿、胎神、
        黄道/黑道十二神、佛历、道历等信息

    Raises:
        ValueError: 日期格式错误或年份超出范围
    """
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，收到: {date!r}")

    if d.year < 1900 or d.year > 2100:
        raise ValueError("Year must be between 1900 and 2100")

    y, m, day = d.year, d.month, d.day

    # 带时辰的 Lunar 对象（供时柱相关 API 使用）
    lunar = Solar.fromYmdHms(y, m, day, hour, 0, 0).getLunar()

    # ── 八字四柱 ──────────────────────────────────────────────
    ba_zi = lunar.getBaZi()                    # 以立春换年
    ba_zi_wu_xing = lunar.getBaZiWuXing()

    year_gan_zhi = lunar.getYearInGanZhi()     # 以正月初一换年
    month_gan_zhi = lunar.getMonthInGanZhi()
    day_gan_zhi = lunar.getDayInGanZhi()
    day_gan = lunar.getDayGan()
    day_zhi = lunar.getDayZhi()

    # ── 纳音五行 ──────────────────────────────────────────────
    year_na_yin = lunar.getYearNaYin()
    month_na_yin = lunar.getMonthNaYin()
    day_na_yin = lunar.getDayNaYin()
    time_na_yin = lunar.getTimeNaYin()

    # ── 二十八宿 ──────────────────────────────────────────────
    xiu = lunar.getXiu()
    xiu_luck = lunar.getXiuLuck()
    xiu_song = lunar.getXiuSong()

    # ── 胎神方位 ──────────────────────────────────────────────
    day_position_tai = lunar.getDayPositionTai()
    month_position_tai: Optional[str] = lunar.getMonthPositionTai() or None

    # ── 黄道/黑道十二神 ───────────────────────────────────────
    tian_shen = lunar.getDayTianShen()
    tian_shen_luck = lunar.getDayTianShenLuck()
    tian_shen_type = lunar.getDayTianShenType()

    # ── 佛历 / 道历（失败时返回 None）────────────────────────
    foto: Optional[str] = None
    try:
        foto_obj = lunar.getFoto()
        foto = str(foto_obj) if foto_obj is not None else None
    except Exception:
        pass

    tao: Optional[str] = None
    try:
        tao_obj = lunar.getTao()
        tao = str(tao_obj) if tao_obj is not None else None
    except Exception:
        pass

    return AdvancedInfo(
        date=date,
        ba_zi=ba_zi,
        ba_zi_wu_xing=ba_zi_wu_xing,
        year_gan_zhi=year_gan_zhi,
        month_gan_zhi=month_gan_zhi,
        day_gan_zhi=day_gan_zhi,
        day_gan=day_gan,
        day_zhi=day_zhi,
        year_na_yin=year_na_yin,
        month_na_yin=month_na_yin,
        day_na_yin=day_na_yin,
        time_na_yin=time_na_yin,
        xiu=xiu,
        xiu_luck=xiu_luck,
        xiu_song=xiu_song,
        day_position_tai=day_position_tai,
        month_position_tai=month_position_tai,
        tian_shen=tian_shen,
        tian_shen_luck=tian_shen_luck,
        tian_shen_type=tian_shen_type,
        foto=foto,
        tao=tao,
    )
