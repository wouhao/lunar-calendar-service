#!/usr/bin/env python3
"""万年历 CLI — 命令行入口"""

from datetime import date

import click


@click.group()
def cli():
    """🌙 万年历服务 CLI

    查询农历、节气、节假日、黄历宜忌等信息。
    """


@cli.command()
def today():
    """查询今日万年历信息（公历 / 农历 / 节气 / 宜忌）"""
    today_date = date.today()
    click.echo(f"📅 今日日期：{today_date.strftime('%Y-%m-%d')}（功能即将实现）")


if __name__ == "__main__":
    cli()
