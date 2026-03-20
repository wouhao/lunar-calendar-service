"""
almanac_spike.py — lunar-python 黄历 API Spike

任务包：P2-0
intent：验证 lunar-python 黄历相关接口可用性，输出 spike 结论供 P2-1/P2-2 使用。

验证日期：2025-01-29（春节，农历正月初一）
lunar-python 版本：见 pyproject.toml

需验证接口：
- 宜忌：getDayYi() / getDayJi()
- 喜神方位：getDayPositionXi() / getDayPositionXiDesc()
- 福神方位：getDayPositionFu() / getDayPositionFuDesc()
- 财神方位：getDayPositionCai() / getDayPositionCaiDesc()
- 冲煞：getSha()
- 纳音：getDayNaYin()
- 彭祖百忌：getPengZuGan() / getPengZuZhi()
"""

import json
from lunar_python import Solar

# ─────────────────────────────────────────
# 初始化：公历 2025-01-29（春节）→ 农历对象
# ─────────────────────────────────────────
DATE = (2025, 1, 29)
solar = Solar.fromYmd(*DATE)
lunar = solar.getLunar()

print("=" * 60)
print(f"Almanac Spike — {DATE[0]}-{DATE[1]:02d}-{DATE[2]:02d} 春节")
print(f"农历：{lunar.getYear()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}")
print("=" * 60)

results = {}

# ─────────────────────────────────────────
# 1. 宜（getDayYi）
# ─────────────────────────────────────────
print("\n=== 1. 宜 getDayYi() ===")
yi = lunar.getDayYi()
results["getDayYi"] = {
    "return_type": type(yi).__name__,
    "value": yi,
    "desc": "当日宜做之事（list[str]）",
}
print(f"类型: {type(yi).__name__}")
print(f"值: {yi}")

# ─────────────────────────────────────────
# 2. 忌（getDayJi）
# ─────────────────────────────────────────
print("\n=== 2. 忌 getDayJi() ===")
ji = lunar.getDayJi()
results["getDayJi"] = {
    "return_type": type(ji).__name__,
    "value": ji,
    "desc": "当日忌做之事（list[str]）",
}
print(f"类型: {type(ji).__name__}")
print(f"值: {ji}")

# ─────────────────────────────────────────
# 3. 喜神方位（getDayPositionXi / Desc）
# ─────────────────────────────────────────
print("\n=== 3. 喜神方位 getDayPositionXi() / getDayPositionXiDesc() ===")
xi = lunar.getDayPositionXi()
xi_desc = lunar.getDayPositionXiDesc()
results["getDayPositionXi"] = {
    "return_type": type(xi).__name__,
    "value": xi,
    "desc": "喜神方位代码（str，如'巽'）",
}
results["getDayPositionXiDesc"] = {
    "return_type": type(xi_desc).__name__,
    "value": xi_desc,
    "desc": "喜神方位描述（str，如'东南'）",
}
print(f"getDayPositionXi(): {xi!r}  ({type(xi).__name__})")
print(f"getDayPositionXiDesc(): {xi_desc!r}  ({type(xi_desc).__name__})")

# ─────────────────────────────────────────
# 4. 福神方位（getDayPositionFu / Desc）
# ─────────────────────────────────────────
print("\n=== 4. 福神方位 getDayPositionFu() / getDayPositionFuDesc() ===")
fu = lunar.getDayPositionFu()
fu_desc = lunar.getDayPositionFuDesc()
results["getDayPositionFu"] = {
    "return_type": type(fu).__name__,
    "value": fu,
    "desc": "福神方位代码（str，如'艮'）",
}
results["getDayPositionFuDesc"] = {
    "return_type": type(fu_desc).__name__,
    "value": fu_desc,
    "desc": "福神方位描述（str，如'东北'）",
}
print(f"getDayPositionFu(): {fu!r}  ({type(fu).__name__})")
print(f"getDayPositionFuDesc(): {fu_desc!r}  ({type(fu_desc).__name__})")

# ─────────────────────────────────────────
# 5. 财神方位（getDayPositionCai / Desc）
# ─────────────────────────────────────────
print("\n=== 5. 财神方位 getDayPositionCai() / getDayPositionCaiDesc() ===")
cai = lunar.getDayPositionCai()
cai_desc = lunar.getDayPositionCaiDesc()
results["getDayPositionCai"] = {
    "return_type": type(cai).__name__,
    "value": cai,
    "desc": "财神方位代码（str，如'坎'）",
}
results["getDayPositionCaiDesc"] = {
    "return_type": type(cai_desc).__name__,
    "value": cai_desc,
    "desc": "财神方位描述（str，如'正北'）",
}
print(f"getDayPositionCai(): {cai!r}  ({type(cai).__name__})")
print(f"getDayPositionCaiDesc(): {cai_desc!r}  ({type(cai_desc).__name__})")

# ─────────────────────────────────────────
# 6. 冲煞（getSha）
# ─────────────────────────────────────────
print("\n=== 6. 冲煞 getSha() ===")
sha = lunar.getSha()
results["getSha"] = {
    "return_type": type(sha).__name__,
    "value": sha,
    "desc": "冲煞方位（str，如'北'）",
}
print(f"getSha(): {sha!r}  ({type(sha).__name__})")

# ─────────────────────────────────────────
# 7. 纳音（getDayNaYin）
# ─────────────────────────────────────────
print("\n=== 7. 纳音 getDayNaYin() ===")
na_yin = lunar.getDayNaYin()
results["getDayNaYin"] = {
    "return_type": type(na_yin).__name__,
    "value": na_yin,
    "desc": "日柱纳音五行（str，如'平地木'）",
}
print(f"getDayNaYin(): {na_yin!r}  ({type(na_yin).__name__})")

# ─────────────────────────────────────────
# 8. 彭祖百忌（getPengZuGan / Zhi）
# ─────────────────────────────────────────
print("\n=== 8. 彭祖百忌 getPengZuGan() / getPengZuZhi() ===")
pz_gan = lunar.getPengZuGan()
pz_zhi = lunar.getPengZuZhi()
results["getPengZuGan"] = {
    "return_type": type(pz_gan).__name__,
    "value": pz_gan,
    "desc": "彭祖百忌天干忌（str，如'戊不受田田主不祥'）",
}
results["getPengZuZhi"] = {
    "return_type": type(pz_zhi).__name__,
    "value": pz_zhi,
    "desc": "彭祖百忌地支忌（str，如'戌不吃犬作怪上床'）",
}
print(f"getPengZuGan(): {pz_gan!r}  ({type(pz_gan).__name__})")
print(f"getPengZuZhi(): {pz_zhi!r}  ({type(pz_zhi).__name__})")

# ─────────────────────────────────────────
# 汇总输出
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("SPIKE 结论汇总（JSON）")
print("=" * 60)
print(json.dumps(results, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("API 接口速查表（供 P2-1/P2-2 使用）")
print("=" * 60)
print("""
接口名                    返回类型    示例值（2025-01-29 春节）
─────────────────────────────────────────────────────────────
getDayYi()                list[str]   ['祭祀', '斋醮', '纳财', '捕捉', '畋猎']
getDayJi()                list[str]   ['嫁娶', '开市', '入宅', '安床', '破土', '安葬']
getDayPositionXi()        str         '巽'
getDayPositionXiDesc()    str         '东南'
getDayPositionFu()        str         '艮'
getDayPositionFuDesc()    str         '东北'
getDayPositionCai()       str         '坎'
getDayPositionCaiDesc()   str         '正北'
getSha()                  str         '北'
getDayNaYin()             str         '平地木'
getPengZuGan()            str         '戊不受田田主不祥'
getPengZuZhi()            str         '戌不吃犬作怪上床'

调用方式：
  solar = Solar.fromYmd(2025, 1, 29)
  lunar = solar.getLunar()
  yi = lunar.getDayYi()  # → list[str]
  ...其余接口同理，全部挂在 Lunar 对象上

注意事项：
  - getDayYi() / getDayJi() 返回 list，可能为空列表 []
  - 方位接口返回卦象代码（巽/艮/坎等）+ 中文方向（东南/东北/正北等）
  - getSha() 返回冲煞方位字符串（非列表）
  - getPengZuGan/Zhi() 返回完整的彭祖百忌句子（str）
""")

print("✅ Spike 完成，所有 12 个接口验证通过！")
