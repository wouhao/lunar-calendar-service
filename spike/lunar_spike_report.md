# lunar-python Spike 验证报告

**版本：** lunar-python 1.4.8  
**测试日期：** 2026-03-20  
**结论：** ✅ 第一梯队功能均可由 lunar-python 覆盖

---

## 环境

```
pip install lunar-python==1.4.8
from lunar_python import Solar, Lunar, LunarMonth
```

---

## 测试结果

### 1. 公历 → 农历转换

**测试用例：** 2024-02-10（春节）

```json
{
  "solar": "2024-02-10",
  "lunar_year": 2024,
  "lunar_month": 1,
  "lunar_day": 1,
  "lunar_year_chinese": "二〇二四",
  "lunar_month_chinese": "正",
  "lunar_day_chinese": "初一",
  "lunar_str": "二〇二四年正月初一"
}
```

**接口：** `Solar.fromYmd(y, m, d).getLunar()`  
**状态：** ✅ 正常

---

### 2. 农历 → 公历转换

**测试用例：** 农历2024年正月初一 → 公历

```json
{
  "lunar": "农历2024年正月初一",
  "solar_str": "2024-02-10",
  "weekday": "六"
}
```

**接口：** `Lunar.fromYmd(y, m, d).getSolar()`  
**状态：** ✅ 正常

---

### 3a. 某天节气查询

**测试用例：** 2024-03-20（春分）

```json
{
  "date": "2024-03-20",
  "jieqi_name": "春分",
  "current_jieqi_obj": "春分"
}
```

**接口：** `lunar.getJieQi()` / `lunar.getCurrentJieQi()`  
**说明：** 若当天是节气则返回名称，否则返回空字符串/None  
**状态：** ✅ 正常

---

### 3b. 下一个节气查询

**测试用例：** 从2024-03-01起的下一个节气

```json
{
  "from_date": "2024-03-01",
  "next_name": "惊蛰",
  "next_date": "2024-03-05",
  "is_jie": true,
  "is_qi": false
}
```

**接口：** `lunar.getNextJieQi()` 返回 `JieQi` 对象，含 `getName()`、`getSolar()`、`isJie()`、`isQi()`  
**状态：** ✅ 正常

---

### 4. 干支（年/月/日）

**测试用例：** 2024-02-10（甲辰龙年）

```json
{
  "date": "2024-02-10",
  "year_ganzhi": "甲辰",
  "month_ganzhi": "丙寅",
  "day_ganzhi": "甲辰",
  "year_gan": "甲",
  "year_zhi": "辰"
}
```

**接口：** `lunar.getYearInGanZhi()` / `getMonthInGanZhi()` / `getDayInGanZhi()`  
**状态：** ✅ 正常

---

### 5. 生肖

**测试用例：** 2024-02-10

```json
{
  "date": "2024-02-10",
  "year_shengxiao": "龙",
  "month_shengxiao": "虎",
  "day_shengxiao": "龙",
  "animal": "貉"
}
```

**接口：** `lunar.getYearShengXiao()` / `getMonthShengXiao()` / `getDayShengXiao()`  
**说明：** `getAnimal()` 返回精确生肖（含貉等细分），与 `getYearShengXiao()` 略有差异  
**状态：** ✅ 正常

---

### 6. 星座

**测试用例：** 多日期

```json
{
  "date": "2024-02-10",
  "xingzuo": "水瓶",
  "samples": [
    { "date": "2024-01-20", "xingzuo": "水瓶" },
    { "date": "2024-03-21", "xingzuo": "白羊" },
    { "date": "2024-06-21", "xingzuo": "双子" }
  ]
}
```

**接口：** `Solar.fromYmd(y, m, d).getXingZuo()`  
**状态：** ✅ 正常

---

## 功能覆盖汇总

| 功能 | 接口 | 状态 |
|------|------|------|
| 公历 → 农历 | `Solar.fromYmd().getLunar()` | ✅ |
| 农历 → 公历 | `Lunar.fromYmd().getSolar()` | ✅ |
| 当天节气 | `lunar.getJieQi()` / `getCurrentJieQi()` | ✅ |
| 下一个节气 | `lunar.getNextJieQi()` | ✅ |
| 干支（年月日） | `getYearInGanZhi()` / `getMonthInGanZhi()` / `getDayInGanZhi()` | ✅ |
| 生肖 | `getYearShengXiao()` | ✅ |
| 星座 | `Solar.getXingZuo()` | ✅ |

---

## 备注 & 注意事项

1. **导入方式：** `from lunar_python import Solar, Lunar`（不是 `import Lunar`）
2. **闰月处理：** 农历闰月用负数月份表示，例如 `Lunar.fromYmd(2020, -4, 1)` 表示闰四月初一；通过 `LunarMonth.fromYm(y, -m).isLeap()` 可判断
3. **节气 API 区别：**
   - `getJieQi()` → 字符串，当天是节气返回名称，否则空字符串
   - `getCurrentJieQi()` → 返回 JieQi 对象或 None
   - `getNextJieQi()` → 总是返回下一个节气的 JieQi 对象
4. **生肖 vs Animal：** `getAnimal()` 返回更精确的传统名称（如"貉"代替"龙"），`getYearShengXiao()` 返回标准十二生肖名
5. **星座名称：** 返回中文简写（如"水瓶"、"白羊"），不含"座"字

---

**结论：** lunar-python 1.4.8 完整覆盖第一梯队需求，API 设计清晰，可作为后端日历服务的核心依赖。
