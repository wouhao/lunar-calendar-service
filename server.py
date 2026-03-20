"""
Lunar Calendar MCP Server
使用 mcp SDK 提供万年历相关工具
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lunar-calendar-service")


@mcp.tool()
def get_date_info(date: str) -> str:
    """获取指定日期的详细信息（阳历/阴历/节气/节假日等）。
    
    Args:
        date: 日期字符串，格式 YYYY-MM-DD
    """
    return "not implemented"


@mcp.tool()
def solar_to_lunar(date: str) -> str:
    """阳历转阴历。
    
    Args:
        date: 阳历日期字符串，格式 YYYY-MM-DD
    """
    return "not implemented"


@mcp.tool()
def lunar_to_solar(year: int, month: int, day: int, leap_month: bool = False) -> str:
    """阴历转阳历。
    
    Args:
        year: 阴历年份
        month: 阴历月份（1-12）
        day: 阴历日（1-30）
        leap_month: 是否为闰月，默认 False
    """
    return "not implemented"


@mcp.tool()
def get_solar_terms(year: int) -> str:
    """获取指定年份的全部节气日期。
    
    Args:
        year: 年份，如 2024
    """
    return "not implemented"


@mcp.tool()
def is_holiday(date: str) -> str:
    """判断指定日期是否为节假日。
    
    Args:
        date: 日期字符串，格式 YYYY-MM-DD
    """
    return "not implemented"


@mcp.tool()
def get_holidays(year: int) -> str:
    """获取指定年份的全部节假日列表。
    
    Args:
        year: 年份，如 2024
    """
    return "not implemented"


if __name__ == "__main__":
    mcp.run()
