# Phase 1 Fix Review v1

**entity_id:** review-20260320-p1-fix  
**parent_task_id:** task-20260320-001  
**reviewer:** Claude Code (Reviewer subagent)  
**review date:** 2026-03-20  
**target commit:** 1e60d9b

---

## 概述

验证 Codex 对 Phase 1 Review 发现的 4 个问题（B1、Fix-2、Fix-3、Fix-4）的修复是否正确。

---

## 逐项验证结果

### B1 — is_holiday 静默降级修复

**问题描述：** 原实现在缺少节假日数据时返回"普通工作日"，掩盖了数据缺失这一事实。

**验证 1：`is_holiday("2026-03-20")` 应返回含 error 字段的 dict**

```python
>>> is_holiday("2026-03-20")
{
  'date': '2026-03-20',
  'is_holiday': None,
  'is_workday': None,
  'holiday_name': None,
  'note': None,
  'error': 'No holiday data for year 2026'
}
```

✅ **通过** — 返回了含 `error` 字段的 dict，`is_holiday` 和 `is_workday` 均为 `None`，不再返回"普通工作日"。

**验证 2：`get_date_info("2026-03-20")` 的 is_holiday/is_workday 字段应为 None，含 holiday_data_available: false**

```python
>>> info = get_date_info("2026-03-20")
>>> info.is_holiday     # None
>>> info.is_workday     # None
>>> info.holiday_data_available  # False
```

✅ **通过** — `is_holiday=None`，`is_workday=None`，`holiday_data_available=False`，正确透传数据缺失状态。

**验证 3：DateInfo model 的 is_holiday/is_workday 是否正确改为 Optional[bool]**

```python
# models/date_info.py
is_holiday: Optional[bool] = None
is_workday: Optional[bool] = None
```

```python
>>> typing.get_type_hints(DateInfo)['is_holiday']
typing.Optional[bool]
>>> typing.get_type_hints(DateInfo)['is_workday']
typing.Optional[bool]
```

✅ **通过** — 两个字段类型均正确改为 `Optional[bool]`，默认值为 `None`。

---

### Fix-2 — 重阳节数据错误修复

**问题描述：** 重阳节是农历九月初九，不是阳历节日，不应出现在 `_SOLAR_FESTIVALS` 中。

**验证：`_SOLAR_FESTIVALS` 中不再有 `(9, 9, "重阳节（阳历）")`**

```python
>>> (9, 9, "重阳节（阳历）") in _SOLAR_FESTIVALS
False
```

9 月的阳历节日仅剩：
```
(9, 10, '教师节')
```

重阳节已正确移至 `_LUNAR_FESTIVALS`：
```python
_LUNAR_FESTIVALS = [
    ...
    (9, 9, "重阳节"),
    ...
]
```

✅ **通过** — 重阳节已从 `_SOLAR_FESTIVALS` 删除，保留在 `_LUNAR_FESTIVALS` 中，数据正确。

---

### Fix-3 — 除夕动态判断

**问题描述：** 原实现硬编码腊月 30 为除夕，无法处理无腊月三十的年份（腊月只有 29 天）。

**验证 1：`get_date_info("2022-01-31")` 的 festivals 含"除夕"（2022年腊月29天）**

```python
>>> get_date_info("2022-01-31").festivals
['除夕']
```

✅ **通过** — 2022-01-31 是农历壬寅年腊月二十九（当年腊月共 29 天），动态判断正确识别为除夕。

**验证 2：`get_date_info("2025-01-28")` 的 festivals 含"除夕"（2025年腊月29天）**

```python
>>> get_date_info("2025-01-28").festivals
['除夕']
```

✅ **通过** — 2025-01-28 是农历甲辰年腊月二十九（当年腊月共 29 天），动态判断正确识别为除夕。

**实现方式：** `_is_chuxi()` 函数通过检查"明天的农历月份是否变为正月（1月）"来动态判断，比硬编码腊月 30 更为健壮。

---

### Fix-4 — lunar_to_solar 返回格式

**问题描述：** 原 `server.py` 的 `lunar_to_solar` 工具直接返回裸字符串，不符合 JSON 结构化格式约定。

**验证：server.py 中 lunar_to_solar 工具返回 JSON `{"solar_date": "..."}`**

```python
# server.py
@mcp.tool()
def lunar_to_solar(year: int, month: int, day: int, leap_month: bool = False) -> str:
    result = _lunar_to_solar(year, month, day, leap_month)
    return json.dumps({"solar_date": result}, ensure_ascii=False)
```

调用示例：
```python
# 底层 service 返回裸字符串
>>> lunar_to_solar(2025, 1, 1)
"2025-01-29"

# server.py 包装后输出
>>> '{"solar_date": "2025-01-29"}'
```

✅ **通过** — server.py 使用 `json.dumps({"solar_date": result})` 包装，返回结构化 JSON，格式符合要求。

---

## 测试状态

运行 `uv run pytest tests/ -v`：

```
tests/test_date_service.py::test_get_date_info PASSED
tests/test_date_service.py::test_solar_to_lunar PASSED
tests/test_date_service.py::test_lunar_to_solar PASSED
tests/test_date_service.py::test_get_solar_terms PASSED
tests/test_date_service.py::test_is_holiday_holiday PASSED
tests/test_date_service.py::test_is_holiday_workday PASSED
tests/test_date_service.py::test_get_holidays PASSED
tests/test_placeholder.py::test_placeholder PASSED

8 passed in 0.25s
```

✅ **全部 8 个测试通过，无回归。**

---

## 次要观察（不阻塞收尾）

1. **`holiday_data_available` 默认值为 `True`**：`DateInfo` 模型默认值 `holiday_data_available: bool = True`。当数据可用时正常；当数据不可用时 `get_date_info` 会正确传入 `False`。逻辑无误，但默认值可能让人误解。不影响当前行为，可在后续迭代中改为 `Optional[bool]` 或显式传参。

2. **缺少针对 B1/Fix-3 的专项测试用例**：现有测试未覆盖 `is_holiday("2026-03-20")`（无数据年份）和除夕动态判断场景。建议后续补充，以防回归。

---

## 最终结论

**✅ 4 个修复全部通过**

| 修复项 | 状态 |
|--------|------|
| B1 — is_holiday 静默降级 | ✅ 通过 |
| Fix-2 — 重阳节数据错误 | ✅ 通过 |
| Fix-3 — 除夕动态判断 | ✅ 通过 |
| Fix-4 — lunar_to_solar 返回格式 | ✅ 通过 |

Phase 1 可以正式收尾。
