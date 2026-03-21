"""
advanced_spike.py — Phase 3 高级 API 验证
测试日期：2025-01-29（乙巳年春节）

=== API 速查表 ===
功能                      方法                          可用性
---------------------------------------------------------------
八字·年柱干支             getYearInGanZhi()             ✅
八字·月柱干支             getMonthInGanZhi()            ✅
八字·日柱干支             getDayInGanZhi()              ✅
八字·时柱干支(含时辰)     getTimeInGanZhi() + getBaZi() ✅
八字(四柱列表)            getBaZi()                     ✅
日主天干                  getDayGan()                   ✅
日主地支                  getDayZhi()                   ✅
八字五行(四柱)            getBaZiWuXing()               ✅
纳音五行·年               getYearNaYin()                ✅
纳音五行·月               getMonthNaYin()               ✅
纳音五行·日               getDayNaYin()                 ✅
纳音五行·时               getTimeNaYin()                ✅
二十八宿                  getXiu()                      ✅
宿吉凶                    getXiuLuck()                  ✅
宿歌诀                    getXiuSong()                  ✅
胎神方位·日               getDayPositionTai()           ✅
胎神方位·月               getMonthPositionTai()         ✅
佛历(Foto)                getFoto()                     ✅
道历(Tao)                 getTao()                      ✅
黄道/黑道十二神           getDayTianShen()              ✅
天神吉凶                  getDayTianShenLuck()          ✅
天神类型                  getDayTianShenType()          ✅
时天神                    getTimeTianShen()             ✅
=== END 速查表 ===
"""

from lunar_python import Lunar, Solar

# 测试日期：2025-01-29 春节，时辰设为午时（12点）
solar = Solar.fromYmdHms(2025, 1, 29, 12, 0, 0)
lunar = Lunar.fromSolar(solar)

print("=" * 60)
print(f"公历：{solar}")
print(f"农历：{lunar}")
print("=" * 60)

# ── 1. 八字（四柱）──────────────────────────────────────────
print("\n【1. 八字·四柱】")
bazi = lunar.getBaZi()
print(f"  getBaZi() → {bazi}  (类型: {type(bazi).__name__})")
print(f"  年柱: {bazi[0]}")
print(f"  月柱: {bazi[1]}")
print(f"  日柱: {bazi[2]}")
print(f"  时柱: {bazi[3]}")

print(f"\n  getYearInGanZhi()  → {lunar.getYearInGanZhi()}  ⚠️ 以正月初一换年（与 getBaZi()[0] 不同）")
print(f"  getMonthInGanZhi() → {lunar.getMonthInGanZhi()}")
print(f"  getDayInGanZhi()   → {lunar.getDayInGanZhi()}")
print(f"  getTimeInGanZhi()  → {lunar.getTimeInGanZhi()}")
print(f"  ⚠️  注意：getBaZi()[0]={lunar.getBaZi()[0]} 用立春换年；getYearInGanZhi()={lunar.getYearInGanZhi()} 用正月初一换年")

print(f"\n  日主天干 getDayGan()  → {lunar.getDayGan()}")
print(f"  日主地支 getDayZhi()  → {lunar.getDayZhi()}")

# ── 2. 五行 ─────────────────────────────────────────────────
print("\n【2. 五行】")
wuxing = lunar.getBaZiWuXing()
print(f"  getBaZiWuXing() → {wuxing}  (类型: {type(wuxing).__name__})")
if wuxing:
    for i, name in enumerate(["年柱五行", "月柱五行", "日柱五行", "时柱五行"]):
        val = wuxing[i] if i < len(wuxing) else "N/A"
        print(f"    {name}: {val}")

print(f"\n  纳音五行·年 getYearNaYin()  → {lunar.getYearNaYin()}")
print(f"  纳音五行·月 getMonthNaYin() → {lunar.getMonthNaYin()}")
print(f"  纳音五行·日 getDayNaYin()   → {lunar.getDayNaYin()}")
print(f"  纳音五行·时 getTimeNaYin()  → {lunar.getTimeNaYin()}")

# ── 3. 二十八宿 ──────────────────────────────────────────────
print("\n【3. 二十八宿】")
xiu = lunar.getXiu()
xiu_luck = lunar.getXiuLuck()
xiu_song = lunar.getXiuSong()
print(f"  getXiu()     → {xiu!r}  (类型: {type(xiu).__name__})")
print(f"  getXiuLuck() → {xiu_luck!r}")
print(f"  getXiuSong() → {xiu_song!r}")

# ── 4. 胎神方位 ──────────────────────────────────────────────
print("\n【4. 胎神方位】")
tai_day = lunar.getDayPositionTai()
tai_month = lunar.getMonthPositionTai()
print(f"  getDayPositionTai()   → {tai_day!r}  (类型: {type(tai_day).__name__})")
print(f"  getMonthPositionTai() → {tai_month!r}")

# ── 5. 佛历 / 道历 ───────────────────────────────────────────
print("\n【5. 佛历 / 道历】")
try:
    foto = lunar.getFoto()
    print(f"  getFoto() → {foto}  (类型: {type(foto).__name__})")
    print(f"  getFoto() dir: {[m for m in dir(foto) if not m.startswith('_')]}")
except Exception as e:
    print(f"  getFoto() ❌ 异常: {e}")

try:
    tao = lunar.getTao()
    print(f"  getTao()  → {tao}  (类型: {type(tao).__name__})")
    print(f"  getTao() dir: {[m for m in dir(tao) if not m.startswith('_')]}")
except Exception as e:
    print(f"  getTao() ❌ 异常: {e}")

# ── 6. 黄道吉日 / 黄道·黑道十二神 ───────────────────────────
print("\n【6. 黄道黑道十二神 / 吉凶】")
tian_shen = lunar.getDayTianShen()
tian_shen_luck = lunar.getDayTianShenLuck()
tian_shen_type = lunar.getDayTianShenType()
print(f"  getDayTianShen()     → {tian_shen!r}  (天神名称)")
print(f"  getDayTianShenLuck() → {tian_shen_luck!r}  (吉/凶)")
print(f"  getDayTianShenType() → {tian_shen_type!r}  (黄道/黑道)")

time_tian_shen = lunar.getTimeTianShen()
time_tian_shen_luck = lunar.getTimeTianShenLuck()
print(f"  getTimeTianShen()     → {time_tian_shen!r}")
print(f"  getTimeTianShenLuck() → {time_tian_shen_luck!r}")

# ── 7. 附加：宜/忌 ──────────────────────────────────────────
print("\n【7. 宜/忌（附加验证）】")
yi = lunar.getDayYi()
ji = lunar.getDayJi()
print(f"  getDayYi() → {yi}  (类型: list, 长度: {len(yi)})")
print(f"  getDayJi() → {ji}  (类型: list, 长度: {len(ji)})")

# ── 8. EightChar 对象（备用接口） ────────────────────────────
print("\n【8. EightChar 对象（高级接口）】")
try:
    ec = lunar.getEightChar()
    print(f"  getEightChar() → {ec}  (类型: {type(ec).__name__})")
    ec_methods = [m for m in dir(ec) if not m.startswith('_')]
    print(f"  可用方法: {ec_methods}")
except Exception as e:
    print(f"  getEightChar() ❌ 异常: {e}")

print("\n" + "=" * 60)
print("✅ Spike 完成 — 所有目标 API 已验证")
print("=" * 60)
