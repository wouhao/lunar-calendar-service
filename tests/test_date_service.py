import pytest
from services.date_service import (
    get_date_info, solar_to_lunar, lunar_to_solar,
    get_solar_terms, is_holiday, get_holidays
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
