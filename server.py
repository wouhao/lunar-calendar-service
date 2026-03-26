"""
Lunar Calendar MCP Server
使用 mcp SDK 提供万年历相关工具

Transport 模式：
  stdio（默认）: python server.py
  HTTP/SSE:     MCP_TRANSPORT=sse PORT=8000 python server.py
"""

import json
import os
from mcp.server.fastmcp import FastMCP
from services.date_service import (
    get_date_info as _get_date_info,
    solar_to_lunar as _solar_to_lunar,
    lunar_to_solar as _lunar_to_solar,
    get_solar_terms as _get_solar_terms,
    is_holiday as _is_holiday,
    get_holidays as _get_holidays,
    get_almanac as _get_almanac,
    get_advanced_info as _get_advanced_info,
    get_lucky_days as _get_lucky_days,
)

from mcp.server.fastmcp.server import TransportSecuritySettings

mcp = FastMCP(
    "lunar-calendar-service",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


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
    result = _lunar_to_solar(year, month, day, leap_month)
    return json.dumps({"solar_date": result}, ensure_ascii=False)


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


@mcp.tool()
def get_almanac(date: str) -> str:
    """获取指定日期的黄历信息（宜忌、吉神方位、纳音、彭祖百忌等）。
    
    Args:
        date: 日期字符串，格式 YYYY-MM-DD
    """
    result = _get_almanac(date)
    return result.model_dump_json(indent=2)


@mcp.tool()
def get_advanced_info(date: str, hour: int = 12) -> str:
    """获取指定日期的高级信息（八字/五行/星宿/胎神/佛历/道历/黄道黑道）。

    Args:
        date: 日期字符串，格式 YYYY-MM-DD
        hour: 时辰（0-23），默认12（午时），影响八字时柱
    """
    result = _get_advanced_info(date, hour)
    return result.model_dump_json(indent=2)


@mcp.tool()
def get_lucky_days(start_date: str, end_date: str, purpose: str = "") -> str:
    """查询指定日期范围内的黄道吉日。

    Args:
        start_date: 起始日期，格式 YYYY-MM-DD（含）
        end_date:   结束日期，格式 YYYY-MM-DD（含），最多 180 天
        purpose:    可选用途，如"嫁娶"、"开市"；非空时只返回宜列表中含该用途的黄道日
    """
    result = _get_lucky_days(start_date, end_date, purpose or None)
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio")

    if transport == "sse":
        import uvicorn
        from starlette.requests import Request
        from starlette.responses import JSONResponse

        port = int(os.environ.get("PORT", 8000))

        # 获取 Starlette app 并挂载 /health 端点
        app = mcp.sse_app()

        @app.route("/health")
        async def health(request: Request) -> JSONResponse:
            return JSONResponse({"status": "ok", "service": "lunar-calendar-service"})

        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        mcp.run(transport="stdio")
