"""
Lunar Calendar MCP Server
使用 mcp SDK 提供万年历相关工具
"""

import json
from mcp.server.fastmcp import FastMCP
from services.date_service import (
    get_date_info as _get_date_info,
    solar_to_lunar as _solar_to_lunar,
    lunar_to_solar as _lunar_to_solar,
    get_solar_terms as _get_solar_terms,
    is_holiday as _is_holiday,
    get_holidays as _get_holidays,
)

mcp = FastMCP("lunar-calendar-service")


@mcp.tool()
def get_date_info(date: str) -> str:
    """获取指定日期的详细信息（阳历/阴历/节气/节假日等）。
    
    Args:
        date: 日期字符串，格式 YYYY-MM-DD
    """
    result = _get_date_info(date)
    return result.model_dump_json(indent=2)


@mcp.tool()
def solar_to_lunar(date: str) -> str:
    """阳历转阴历。
    
    Args:
        date: 阳历日期字符串，格式 YYYY-MM-DD
    """
    result = _solar_to_lunar(date)
    return result.model_dump_json(indent=2)


@mcp.tool()
def lunar_to_solar(year: int, month: int, day: int, leap_month: bool = False) -> str:
    """阴历转阳历。
    
    Args:
        year: 阴历年份
        month: 阴历月份（1-12）
        day: 阴历日（1-30）
        leap_month: 是否为闰月，默认 False
    """
    return _lunar_to_solar(year, month, day, leap_month)


@mcp.tool()
def get_solar_terms(year: int) -> str:
    """获取指定年份的全部节气日期。
    
    Args:
        year: 年份，如 2024
    """
    result = _get_solar_terms(year)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def is_holiday(date: str) -> str:
    """判断指定日期是否为节假日。
    
    Args:
        date: 日期字符串，格式 YYYY-MM-DD
    """
    result = _is_holiday(date)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_holidays(year: int) -> str:
    """获取指定年份的全部节假日列表。
    
    Args:
        year: 年份，如 2024
    """
    result = _get_holidays(year)
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
