"""
lunar-python spike test
验证 lunar-python 1.4.8 的核心接口可用性
覆盖：公历→农历、农历→公历、节气、干支、生肖、星座
"""

import json
from lunar_python import Solar, Lunar, LunarMonth

results = {}

# ─────────────────────────────────────────
# 1. 公历 → 农历转换
# ─────────────────────────────────────────
print("=== 1. 公历 → 农历 ===")
solar = Solar.fromYmd(2024, 2, 10)  # 2024年春节（农历大年初一）
lunar = solar.getLunar()
solar_to_lunar = {
    "solar": f"{solar.getYear()}-{solar.getMonth():02d}-{solar.getDay():02d}",
    "lunar_year": lunar.getYear(),
    "lunar_month": lunar.getMonth(),
    "lunar_day": lunar.getDay(),
    "lunar_year_chinese": lunar.getYearInChinese(),
    "lunar_month_chinese": lunar.getMonthInChinese(),
    "lunar_day_chinese": lunar.getDayInChinese(),
    "lunar_str": lunar.toString(),
}
results["solar_to_lunar"] = solar_to_lunar
print(json.dumps(solar_to_lunar, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────
# 2. 农历 → 公历转换
# ─────────────────────────────────────────
print("\n=== 2. 农历 → 公历 ===")
lunar2 = Lunar.fromYmd(2024, 1, 1)   # 农历2024年正月初一
solar2 = lunar2.getSolar()
lunar_to_solar = {
    "lunar": f"农历{lunar2.getYear()}年{lunar2.getMonthInChinese()}月{lunar2.getDayInChinese()}",
    "solar_str": f"{solar2.getYear()}-{solar2.getMonth():02d}-{solar2.getDay():02d}",
    "weekday": solar2.getWeekInChinese(),
}
results["lunar_to_solar"] = lunar_to_solar
print(json.dumps(lunar_to_solar, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────
# 3a. 某天的节气
# ─────────────────────────────────────────
print("\n=== 3a. 某天节气（2024-03-20 春分）===")
solar_jq = Solar.fromYmd(2024, 3, 20)
lunar_jq = solar_jq.getLunar()
jieqi_today = lunar_jq.getJieQi()   # 当天若是节气则返回名称，否则空字符串
current_jieqi = lunar_jq.getCurrentJieQi()  # 返回 JieQi 对象或 None
jieqi_on_day = {
    "date": "2024-03-20",
    "jieqi_name": jieqi_today,
    "current_jieqi_obj": current_jieqi.getName() if current_jieqi else None,
}
results["jieqi_on_day"] = jieqi_on_day
print(json.dumps(jieqi_on_day, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────
# 3b. 下一个节气
# ─────────────────────────────────────────
print("\n=== 3b. 下一个节气（从2024-03-01）===")
solar_base = Solar.fromYmd(2024, 3, 1)
lunar_base = solar_base.getLunar()
next_jq = lunar_base.getNextJieQi()  # 返回 JieQi 对象
next_jieqi = {
    "from_date": "2024-03-01",
    "next_name": next_jq.getName() if next_jq else None,
    "next_date": next_jq.getSolar().toString() if next_jq else None,
    "is_jie": next_jq.isJie() if next_jq else None,
    "is_qi": next_jq.isQi() if next_jq else None,
}
results["next_jieqi"] = next_jieqi
print(json.dumps(next_jieqi, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────
# 4. 干支（年/月/日）
# ─────────────────────────────────────────
print("\n=== 4. 干支（年/月/日）===")
solar_gz = Solar.fromYmd(2024, 2, 10)
lunar_gz = solar_gz.getLunar()
ganzhi = {
    "date": "2024-02-10",
    "year_ganzhi": lunar_gz.getYearInGanZhi(),
    "month_ganzhi": lunar_gz.getMonthInGanZhi(),
    "day_ganzhi": lunar_gz.getDayInGanZhi(),
    "year_gan": lunar_gz.getYearGan(),
    "year_zhi": lunar_gz.getYearZhi(),
}
results["ganzhi"] = ganzhi
print(json.dumps(ganzhi, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────
# 5. 生肖
# ─────────────────────────────────────────
print("\n=== 5. 生肖 ===")
shengxiao = {
    "date": "2024-02-10",
    "year_shengxiao": lunar_gz.getYearShengXiao(),    # 年生肖
    "month_shengxiao": lunar_gz.getMonthShengXiao(),  # 月生肖
    "day_shengxiao": lunar_gz.getDayShengXiao(),      # 日生肖
    "animal": lunar_gz.getAnimal(),                    # 生肖（别名）
}
results["shengxiao"] = shengxiao
print(json.dumps(shengxiao, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────
# 6. 星座
# ─────────────────────────────────────────
print("\n=== 6. 星座 ===")
solar_xz = Solar.fromYmd(2024, 2, 10)
xingzuo = {
    "date": "2024-02-10",
    "xingzuo": solar_xz.getXingZuo(),
}
# 多测几个日期
samples = [
    Solar.fromYmd(2024, 1, 20),  # 水瓶座
    Solar.fromYmd(2024, 3, 21),  # 白羊座
    Solar.fromYmd(2024, 6, 21),  # 巨蟹座
]
xingzuo["samples"] = [
    {"date": f"{s.getYear()}-{s.getMonth():02d}-{s.getDay():02d}", "xingzuo": s.getXingZuo()}
    for s in samples
]
results["xingzuo"] = xingzuo
print(json.dumps(xingzuo, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────
# 汇总
# ─────────────────────────────────────────
print("\n\n===== ALL RESULTS =====")
print(json.dumps(results, ensure_ascii=False, indent=2))
print("\n✅ All tests passed!")
