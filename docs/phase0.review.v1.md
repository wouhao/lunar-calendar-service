# Phase 0 综合 Review

**entity_id:** review-20260320-001  
**parent_task_id:** task-20260320-001  
**review 日期：** 2026-03-20  
**reviewer：** Claude Code Reviewer Subagent  
**审查范围：** 仓库 Phase 0 全部产物

---

## 总体评价

Phase 0 骨架已基本就位：核心库（lunar-python）经过 spike 验证可行，PRD 规定的 6 个 MCP 工具签名全部注册，Pydantic schema 覆盖了主要字段，CI 流水线可以运行。但在进入 Phase 1 之前，存在 **3 个 Blocking 问题**（会导致安装或构建直接失败）和若干 Major/Medium 问题需要修复或明确。

---

## 各产物逐项评审

### 1. spike/lunar_test.py + spike/lunar_spike_report.md

**评分：⭐⭐⭐⭐ 良好，有一处遗漏**

**优点：**
- 覆盖了第一梯队核心功能：公历→农历、农历→公历、当天节气、下一个节气、干支（年月日）、生肖、星座。
- 输出 JSON 格式，测试用例选取典型日期（春节、春分），结果可直接作为文档使用。
- 详细记录了 API 细节（如 `getJieQi()` vs `getCurrentJieQi()` 的区别、闰月负数表示法）。
- 运行结果和报告一致，可信度高。

**问题：**

| 严重程度 | 问题 |
|---------|------|
| **Major** | `get_solar_terms(year) → list` 是 PRD 一级接口，需要获取某年**全部 24 个节气**的日期列表。spike 仅测试了"下一个节气"（`getNextJieQi()`），未验证全年节气枚举 API（如 `lunar.getJieQiTable()` 或遍历方式）。Phase 1 开始前需要补充验证。 |
| **Minor** | 闰月处理（`Lunar.fromYmd(2020, -4, 1)`）在报告中仅作备注，未提供实际可运行测试用例。`lunar_to_solar` 的闰月场景是 PRD 必要参数，建议补充测试。 |
| **Minor** | `getAnimal()` 返回"貉"（非标准十二生肖），报告虽有说明，但建议明确规定 API 实现中统一使用 `getYearShengXiao()` 返回标准生肖，避免用户困惑。 |

---

### 2. models/date_info.py（Pydantic schema）

**评分：⭐⭐⭐ 中等，有结构性缺陷**

**优点：**
- 主要字段已覆盖：solar、lunar（嵌套 LunarDate）、ganzhi（嵌套 GanZhi）、zodiac、constellation、solar_term、festivals、weekday、week_of_year、is_holiday、holiday_name。
- 嵌套模型设计清晰，LunarDate 含 leap 字段可表达闰月。

**问题：**

| 严重程度 | 问题 |
|---------|------|
| **Major** | **`is_workday` 字段缺失。** holidays_2025.json 中存在 `type: "workday"` 类型（调休补班日），这类日期 `is_holiday=False` 但也不是普通工作日。`is_holiday` 字段无法区分"调休上班日"和"普通工作日"，会导致 `is_holiday` 接口语义不完整。建议增加 `is_workday: bool = False`（调班日标记）。 |
| **Medium** | `weekday: int` 编码不明确。Python `date.weekday()` 返回 0=周一~6=周日，ISO 格式 1=周一~7=周日，不同客户端期望不一致。应在字段上加注释或改用 `Literal` / 枚举明确约定。 |
| **Medium** | `LunarDate.label: str` 字段含义未文档化。从 spike 报告看，这应是农历中文全称（如"二〇二四年正月初一"），但未在 schema 中说明。 |
| **Medium** | `zodiac` 字段语义歧义：字面意思是"星座"（Western zodiac），但业务含义是"生肖"（shengxiao）。与 `constellation`（也是星座）并列时极易混淆。建议改名为 `shengxiao` 或添加字段注释 `Field(..., description="生肖，如'龙'")` |
| **Minor** | `festivals: List[str]` 与 `holiday_name: Optional[str]` 存在语义重叠。前者是传统节日列表（春节、元宵等），后者是官方假期名称，应在注释中区分清楚。 |
| **Minor** | `week_of_year: int` 未说明是 ISO week 还是自然周，建议注明。 |

---

### 3. server.py（MCP server 骨架）

**评分：⭐⭐⭐⭐ 良好，签名完整**

**优点：**
- 6 个 PRD 接口全部注册：`get_date_info`、`solar_to_lunar`、`lunar_to_solar`、`get_solar_terms`、`is_holiday`、`get_holidays` ✅
- 参数签名与 PRD 一致：`lunar_to_solar(year, month, day, leap_month=False)` 与 PRD 的 `leap_month` 参数匹配。
- 使用 `FastMCP` 简洁注册，文档字符串清晰。

**问题：**

| 严重程度 | 问题 |
|---------|------|
| **Medium** | 所有工具返回类型均为 `str`。MCP 工具在类型标注为具体模型时，客户端可获得更好的 schema 信息。Phase 1 实现时应将返回类型改为对应 Pydantic 模型（如 `-> DateInfo`、`-> LunarDate`），FastMCP 支持自动序列化。 |
| **Minor** | `leap_month: bool` 与 lunar-python 内部使用负数月份表示闰月（如 `-4` 表示闰四月）的机制不同。Phase 1 实现时需要在接口层做转换：`if leap_month: month = -month`，这个转换逻辑需要明确文档化，避免实现者遗漏。 |

---

### 4. data/holidays_2025.json（节假日数据）

**评分：⭐⭐⭐ 中等，覆盖范围有限**

**优点：**
- 格式设计合理：`{year, source, holidays: [{date, name, type}]}`，来源字段可溯源（国务院通知）。
- 包含调休工作日（`type: "workday"`），能区分"假"与"补班"。
- 2025 年数据按通知内容基本准确（元旦、春节、清明、劳动节、端午、国庆/中秋）。

**问题：**

| 严重程度 | 问题 |
|---------|------|
| **Major** | **数据仅覆盖 2025 年**，但 `get_holidays(year)` 和 `is_holiday(date)` 接口签名支持任意年份。Phase 1 实现若仅依赖 JSON 文件，其他年份调用会返回空或报错。需要在 Phase 1 开始前明确多年数据策略：① 补充历年 JSON 文件，或 ② 对接第三方假期 API 作为兜底。 |
| **Medium** | 端午节数据仅收录 2 天假期（June 1-2），国务院 2025 年通知原文为端午节放假调休共 3 天（5月31日调休，6月1日至2日放假）。实际 6 月 3 日为周二，不放假，故 2 天是正确的。**此条经复核为正常。** 建议增加 JSON 注释或 description 字段说明调休方案，减少后续维护时的疑惑。 |
| **Minor** | 无 JSON schema 文件（如 `data/holidays_schema.json`），数据格式缺乏机器可读规范，后续维护时容易引入格式错误。 |
| **Minor** | `type` 字段目前只有 `"holiday"` 和 `"workday"` 两个值，建议在 README 或 schema 中明确枚举，避免后续出现 `"special"` 等非标准值。 |

---

### 5. .github/workflows/ci.yml（CI 配置）

**评分：⭐⭐⭐ 中等，可运行但覆盖不足**

**优点：**
- 使用 `uv sync + uv run pytest`，工具链现代（uv）。
- push/PR 均触发，基本保护了 main 分支。
- 使用 `actions/checkout@v4` 和 `setup-python@v5`，版本较新。

**问题：**

| 严重程度 | 问题 |
|---------|------|
| **Medium** | 当前只有 `test_placeholder.py`（永远通过），CI 形同虚设，无法发现任何真实问题。Phase 1 需要同步补充真实测试，否则 CI 绿灯没有意义。 |
| **Medium** | 缺少 lint 和类型检查步骤（ruff、mypy），代码质量门禁空缺。建议 Phase 1 同步加入：`uv run ruff check .` 和 `uv run mypy models/`。 |
| **Minor** | 仅测试 Python 3.11，未做 3.12/3.13 兼容性矩阵（`pyproject.toml` 要求 `>=3.11`）。 |
| **Minor** | 没有测试覆盖率报告步骤（`--cov`）。 |

---

### 6. pyproject.toml（依赖配置）

**评分：⭐⭐ 较差，有 Blocking 问题**

**优点：**
- 三个核心依赖（click、lunar-python、mcp）都已列出。
- 使用 `uv.lock` 锁定版本，可复现构建。
- dev 依赖分组清晰（pytest、pytest-asyncio）。

**问题：**

| 严重程度 | 问题 |
|---------|------|
| 🔴 **Blocking** | **`pydantic` 未列为依赖**，但 `models/date_info.py` 中 `from pydantic import BaseModel` 是硬依赖。在纯净环境安装后，`import models.date_info` 会直接报 `ModuleNotFoundError`。 |
| 🔴 **Blocking** | **`hatch.build.targets.wheel.packages = ["src"]`，但项目实际代码在根目录（`server.py`、`cli.py`、`models/`）**。`src/` 目录只有 `.gitkeep`，打包时会产出空 wheel。Phase 1 需要决定：① 将代码移入 `src/lunar_calendar_service/`，或 ② 将 packages 改为 `["."]`（或去掉 hatch 配置，按需调整）。 |
| 🔴 **Blocking** | **lunar-python 版本约束 `>=1.3.12` 与 spike 验证版本 `1.4.8` 不一致**。1.3.x 到 1.4.x 可能有 API 变更（如节气接口），宽松约束下自动安装低版本会导致 spike 验证的 API 无效。建议改为 `>=1.4.8`。 |
| **Minor** | 缺少 `ruff`、`mypy` 等开发工具依赖，CI 中若要加 lint 步骤需先补充。 |
| **Minor** | README.md 仍描述旧技术选型（FastAPI、lunardate/lunarcalendar），与实际选型（FastMCP、lunar-python）不符，容易误导新开发者。 |

---

## 发现问题汇总

### 🔴 Blocking（Phase 1 开始前必须解决）

| # | 位置 | 问题 | 风险 |
|---|------|------|------|
| B-1 | pyproject.toml | `pydantic` 未列为依赖 | 安装后 `import models` 直接崩溃 |
| B-2 | pyproject.toml | 包路径指向空 `src/`，非实际代码位置 | 构建产出空 wheel，打包失败 |
| B-3 | pyproject.toml | `lunar-python>=1.3.12` 与 spike 验证版本 `1.4.8` 不一致 | 低版本 API 不兼容，节气等接口调用失败 |

### 🟡 Major（尽快修复，Phase 1 实现前应明确）

| # | 位置 | 问题 |
|---|------|------|
| M-1 | spike | `get_solar_terms(year)` 全年节气枚举 API 未验证 |
| M-2 | models/date_info.py | 缺少 `is_workday` 字段，调休上班日无法区分 |
| M-3 | data/holidays_2025.json | 仅 2025 年数据，多年查询无数据来源 |

### 🟠 Medium（Phase 1 内解决）

| # | 位置 | 问题 |
|---|------|------|
| Me-1 | models/date_info.py | `zodiac` 命名歧义，建议改 `shengxiao` |
| Me-2 | models/date_info.py | `weekday` 编码未定义 |
| Me-3 | models/date_info.py | `LunarDate.label` 未文档化 |
| Me-4 | server.py | 工具返回类型全为 `str`，应改为 Pydantic 模型 |
| Me-5 | server.py | `leap_month` bool→负月数转换需明确文档 |
| Me-6 | ci.yml | 缺少 lint/type check 步骤 |
| Me-7 | README.md | 技术选型描述过时（FastAPI→MCP，lunardate→lunar-python）|

### 🟢 Minor（建议但不阻塞）

| # | 位置 | 问题 |
|---|------|------|
| Mi-1 | spike | 闰月测试用例未实际运行 |
| Mi-2 | spike | `getAnimal()` vs `getYearShengXiao()` 选择未在实现层明确 |
| Mi-3 | models/date_info.py | `festivals` vs `holiday_name` 语义未区分 |
| Mi-4 | data/ | 缺少 JSON schema 文件 |
| Mi-5 | ci.yml | 仅 Python 3.11，无矩阵测试 |
| Mi-6 | ci.yml | 无覆盖率报告 |

---

## Phase 1 开始前建议（Checklist）

**必须（Blocking 修复）：**
- [ ] `pyproject.toml` 加入 `pydantic>=2.0.0`
- [ ] `pyproject.toml` 修正 `packages` 配置（决定 src layout vs flat layout）
- [ ] `pyproject.toml` 将 `lunar-python` 版本约束改为 `>=1.4.8`

**强烈建议（Major 解决）：**
- [ ] 补充 spike：验证 `get_solar_terms(year)` 全年 24 节气枚举 API
- [ ] `DateInfo` schema 增加 `is_workday: bool = False`
- [ ] 明确多年假期数据策略（补充历年 JSON 或对接 API）

**建议（进入 Phase 1 前评审）：**
- [ ] `DateInfo.zodiac` → `shengxiao`，`weekday` 加编码注释，`LunarDate.label` 加文档
- [ ] 更新 README.md 技术选型描述
- [ ] CI 加入 `ruff check` 步骤，dev deps 加入 ruff/mypy

---

## 总结

Phase 0 骨架方向正确，lunar-python 库选型可行，MCP 工具签名与 PRD 对齐。主要问题集中在**依赖配置**（3个 Blocking）和**数据覆盖范围**（多年假期数据策略未定）。修复 Blocking 问题后，Phase 1 可以安全启动。
