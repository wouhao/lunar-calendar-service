"""
solar_terms_spike.py — lunar-python 节气 API Spike

目标：
1. 验证 lunar-python 中如何获取某年全部 24 节气的日期
2. 返回格式是什么
3. 某天是否是节气如何判断
4. 封装可复用的示例函数

lunar-python 版本：1.4.8
"""

from datetime import date, timedelta
from lunar_python import Lunar, Solar


# =============================================================================
# 封装示例函数
# =============================================================================

def get_solar_terms(year: int) -> list[dict]:
    """
    获取某公历年全部 24 节气列表。

    原理：
    - Lunar.fromYmd(year, 1, 1).getJieQiTable() 返回 dict，key 为节气名（或英文代码），
      value 为 Solar 对象（含精确时刻）。
    - 表里包含约 31 条记录（覆盖当前农历年跨越的所有节气）。
    - 用公历年过滤出属于目标年的节气，再用 Solar 对象的 getLunar().getJieQi()
      取得统一的中文名称（避免 DA_XUE / DONG_ZHI 等英文代码问题）。

    返回：
        list of dict，按日期排序，每条记录格式：
        {
            "date": "YYYY-MM-DD",   # 公历日期
            "name": "节气中文名",    # 如"立春"、"冬至"
            "solar": Solar          # Solar 对象（含精确时刻）
        }
    """
    # 取全年节气表（以该年正月初一为锚点）
    anchor = Lunar.fromYmd(year, 1, 1)
    table = anchor.getJieQiTable()

    results = []
    for _key, solar in table.items():
        if solar.getYear() != year:
            continue
        # 用 getLunar().getJieQi() 拿中文名（比 table 的 key 更可靠）
        chinese_name = solar.getLunar().getJieQi()
        if not chinese_name:
            # 极少数情况 key 是英文代码，直接用 key 的中文映射或跳过
            chinese_name = _key
        results.append({
            "date": f"{solar.getYear()}-{solar.getMonth():02d}-{solar.getDay():02d}",
            "name": chinese_name,
            "solar": solar,
        })

    results.sort(key=lambda x: x["date"])
    return results


def is_solar_term(year: int, month: int, day: int) -> str | None:
    """
    判断某天是否是节气。

    返回：
        节气中文名（如 "立春"），若不是节气则返回 None。

    原理：
        Solar.fromYmd(y, m, d).getLunar().getJieQi() 若当天是节气，
        返回节气名字符串；否则返回空字符串。
    """
    solar = Solar.fromYmd(year, month, day)
    name = solar.getLunar().getJieQi()
    return name if name else None


# =============================================================================
# Spike 验证 —— 输出 2025 年全部 24 节气
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("2025 年 24 节气列表")
    print("=" * 50)

    terms = get_solar_terms(2025)
    for i, t in enumerate(terms, 1):
        solar = t["solar"]
        exact_time = f"{solar.getHour():02d}:{solar.getMinute():02d}:{solar.getSecond():02d}"
        print(f"{i:2d}. {t['date']}  {exact_time}  {t['name']}")

    print()
    print(f"共 {len(terms)} 个节气")

    print()
    print("=" * 50)
    print("验证：is_solar_term() 判断示例")
    print("=" * 50)

    test_cases = [
        (2025, 2, 3),   # 立春
        (2025, 2, 4),   # 非节气
        (2025, 12, 21), # 冬至
        (2025, 4, 4),   # 清明
        (2025, 6, 21),  # 夏至
        (2025, 1, 1),   # 元旦（非节气）
    ]

    for y, m, d in test_cases:
        name = is_solar_term(y, m, d)
        tag = f"✅ {name}" if name else "❌ 非节气"
        print(f"  {y}-{m:02d}-{d:02d}  {tag}")

    print()
    print("=" * 50)
    print("API 总结")
    print("=" * 50)
    print("""
核心 API（lunar-python 1.4.8）：

1. 获取全年节气表：
   anchor = Lunar.fromYmd(year, 1, 1)
   table = anchor.getJieQiTable()
   → 返回 dict[str, Solar]，key 为节气名/英文代码，value 为 Solar 对象
   → Solar 对象含精确时刻（年月日时分秒）

2. 过滤目标公历年：
   for _key, solar in table.items():
       if solar.getYear() == year: ...

3. 获取节气中文名（比 table key 更可靠）：
   solar.getLunar().getJieQi()
   → 返回 str（如 "立春"），若当天不是节气则返回 ""

4. 判断某天是否是节气：
   Solar.fromYmd(y, m, d).getLunar().getJieQi()
   → 非空 → 是节气；空字符串 → 不是节气

注意事项：
- getJieQiTable() 约返回 31 条记录（跨前后农历年），需按公历年过滤
- table 的 key 某些情况下是英文代码（如 DA_XUE、DONG_ZHI），
  改用 getLunar().getJieQi() 可稳定获取中文名
- Lunar.JIE_QI 是 24 节气中文名元组（顺序从冬至开始）
- Lunar.JIE_QI_IN_USE 是包含英文代码在内的全部 31 个 key 元组
""")
