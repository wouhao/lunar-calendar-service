import pytest
from services.date_service import (
    get_date_info, solar_to_lunar, lunar_to_solar,
    get_solar_terms, is_holiday, get_holidays, get_almanac,
    get_advanced_info, get_lucky_days,
)

def test_get_date_info():
    r = get_date_info("2025-01-29")
    assert r.lunar.label == "正月初一"
    assert r.ganzhi.year == "乙巳"
    assert r.is_holiday == True
    assert r.holiday_name == "春节"
    assert r.zodiac == "蛇"

def test_solar_to_lunar():
    r = solar_to_lunar("2025-01-29")
    assert r.month == 1
    assert r.day == 1
    assert r.leap == False

def test_lunar_to_solar():
    r = lunar_to_solar(2025, 1, 1)
    assert r == "2025-01-29"

def test_get_solar_terms():
    terms = get_solar_terms(2025)
    assert len(terms) == 24
    assert terms[0]["name"] == "小寒"

def test_is_holiday_holiday():
    r = is_holiday("2025-01-29")
    assert r["is_holiday"] == True

def test_is_holiday_workday():
    r = is_holiday("2025-01-26")
    assert r["is_workday"] == True

def test_get_holidays():
    r = get_holidays(2025)
    assert len(r["holidays"]) > 0

def test_is_holiday_no_data_year():
    """B1: 无节假日数据年份应返回 error，不静默降级"""
    r = is_holiday("2026-03-20")
    assert "error" in r
    assert r.get("is_holiday") is None

def test_get_date_info_no_data_year():
    """B1: get_date_info 无节假日数据年份，is_holiday/is_workday 为 None"""
    r = get_date_info("2026-03-20")
    assert r.is_holiday is None
    assert r.is_workday is None

def test_chuxi_29_day_month():
    """Fix-3: 腊月29天的年份，除夕正确落在腊月二十九"""
    # 2022年腊月29天，除夕 = 2022-01-31
    r1 = get_date_info("2022-01-31")
    assert "除夕" in r1.festivals
    # 2025年腊月29天，除夕 = 2025-01-28
    r2 = get_date_info("2025-01-28")
    assert "除夕" in r2.festivals

def test_get_almanac():
    r = get_almanac("2025-01-29")
    assert len(r.yi) >= 1
    assert len(r.ji) > 0
    assert r.sha_wei != ""
    assert r.day_na_yin != ""
    assert "平地木" in r.day_na_yin
    assert "祭祀" in r.yi
    assert r.peng_zu_gan != ""
    assert r.peng_zu_zhi != ""
    assert r.position_xi != ""
    assert r.date == "2025-01-29"
    # Fix-3: position_fu/cai 及 desc 非空
    assert r.position_fu != ""
    assert r.position_fu_desc != ""
    assert r.position_cai != ""
    assert r.position_cai_desc != ""


def test_get_almanac_invalid_date():
    with pytest.raises((ValueError, Exception)):
        get_almanac("not-a-date")


# ─────────────────────────────────────────
# Phase 3 Tests: get_advanced_info
# ─────────────────────────────────────────

def test_get_advanced_info():
    """基础测试：2025-01-29 春节"""
    r = get_advanced_info("2025-01-29")
    assert r.date == "2025-01-29"
    assert len(r.ba_zi) == 4
    assert r.xiu != ""
    assert r.tian_shen != ""
    assert r.tian_shen_type in ("黄道", "黑道")
    assert r.day_position_tai != ""


def test_get_advanced_info_with_hour():
    """验证 hour 参数影响八字时柱"""
    r0 = get_advanced_info("2025-01-29", hour=0)
    r12 = get_advanced_info("2025-01-29", hour=12)
    # 时柱是 ba_zi[3]，子时(hour=0) vs 午时(hour=12) 必定不同
    assert r0.ba_zi[3] != r12.ba_zi[3]


def test_get_advanced_info_invalid_date():
    """日期格式错误应 raise ValueError"""
    with pytest.raises(ValueError):
        get_advanced_info("not-a-date")


def test_get_advanced_info_boundary_year():
    """年份超出边界应 raise ValueError"""
    with pytest.raises(ValueError):
        get_advanced_info("1899-12-31")
    with pytest.raises(ValueError):
        get_advanced_info("2101-01-01")


def test_get_advanced_info_foto_tao():
    """佛历/道历字段非 None"""
    r = get_advanced_info("2025-01-29")
    assert r.foto is not None and r.foto != ""
    assert r.tao is not None and r.tao != ""


# ─────────────────────────────────────────
# Phase 3 Tests: get_lucky_days
# ─────────────────────────────────────────

def test_get_lucky_days_with_purpose():
    """带用途过滤：嫁娶"""
    result = get_lucky_days("2025-01-01", "2025-01-31", "嫁娶")
    assert isinstance(result, list)
    assert len(result) > 0
    for item in result:
        assert item["tian_shen_type"] == "黄道"
        assert "嫁娶" in item["yi"]


def test_get_lucky_days_no_purpose():
    """无用途时只按黄道过滤"""
    result = get_lucky_days("2025-01-01", "2025-01-31")
    assert isinstance(result, list)
    assert len(result) > 0
    for item in result:
        assert item["tian_shen_type"] == "黄道"
        assert "date" in item
        assert "tian_shen" in item
        assert "yi" in item


def test_get_lucky_days_exceed_180():
    """超过 180 天应 raise ValueError"""
    with pytest.raises(ValueError, match="180"):
        get_lucky_days("2025-01-01", "2025-09-01")


def test_get_lucky_days_invalid_date():
    """日期格式错误应 raise ValueError"""
    with pytest.raises(ValueError):
        get_lucky_days("bad-date", "2025-01-31")
