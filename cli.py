#!/usr/bin/env python3
"""万年历 CLI — 命令行入口"""

from datetime import date

import click


WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def format_date_info(info) -> str:
    """将 DateInfo 格式化为友好的中文文本。"""
    lines = []

    # 公历日期
    weekday_cn = WEEKDAY_CN[info.weekday - 1]
    lines.append(f"📅 公历：{info.solar}  {weekday_cn}  第 {info.week_of_year} 周")

    # 农历日期
    lunar = info.lunar
    leap_str = "（闰月）" if lunar.leap else ""
    lines.append(
        f"🌙 农历：{lunar.year} 年 {lunar.month} 月{leap_str}  {lunar.label}"
    )

    # 干支
    gz = info.ganzhi
    lines.append(f"🀄 干支：{gz.year}年  {gz.month}月  {gz.day}日")

    # 生肖 & 星座
    lines.append(f"🐾 生肖：{info.zodiac}  ✨ 星座：{info.constellation}")

    # 节气（如有）
    if info.solar_term:
        lines.append(f"🌿 节气：{info.solar_term}")

    # 节日（如有）
    if info.festivals:
        lines.append(f"🎉 节日：{'、'.join(info.festivals)}")

    # 节假日状态
    if info.is_holiday:
        name = f"（{info.holiday_name}）" if info.holiday_name else ""
        lines.append(f"🏖  假日：今天放假 {name}")
    elif info.is_workday:
        lines.append("💼 假日：今天调休上班")
    else:
        weekday = info.weekday
        if weekday >= 6:
            lines.append("😌 假日：普通周末")
        else:
            lines.append("💼 假日：普通工作日")

    return "\n".join(lines)


@click.group()
def cli():
    """🌙 万年历服务 CLI

    查询农历、节气、节假日、黄历宜忌等信息。
    """


@cli.command()
def today():
    """查询今日万年历信息（公历 / 农历 / 节气 / 宜忌）"""
    from services.date_service import get_date_info

    today_date = date.today()
    date_str = today_date.strftime("%Y-%m-%d")

    try:
        info = get_date_info(date_str)
    except ValueError as e:
        click.echo(f"⚠️  获取日期信息失败：{e}", err=True)
        raise click.Abort()

    click.echo(format_date_info(info))


if __name__ == "__main__":
    cli()
