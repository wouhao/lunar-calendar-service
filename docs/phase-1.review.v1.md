# Phase -1 方案 Review

**entity_id:** review-20260320-phase-1  
**parent_task_id:** task-20260320-001  
**review 日期：** 2026-03-20  
**reviewer：** Claude Code Reviewer Subagent  
**审查范围：** PRD 梳理、技术选型、接口设计方案（补做 Phase -1 方案评审）

---

## 总体评价

方案整体方向正确，核心决策（lunar-python 选型、MCP 服务层、Railway 部署）均有充分依据，可以为后续开发提供正式背书。PRD 功能分层逻辑清晰，第一梯队优先级合理，lunar-python 经 spike 验证已覆盖全部第一梯队需求。

主要风险集中在两处：**DateInfo schema 存在字段语义歧义和缺失**（可修复，不 blocking），以及**节假日静态 JSON 方案在多年数据覆盖上存在运维负担**（决策已确认，建议配套治理机制）。Railway 部署方面有一项需关注的 MCP transport 选择问题，需在 Phase 1 实现前明确。

**结论：方案通过 review，可进入 Phase 1 实现阶段。下列问题在实现过程中修复即可，无 blocking。**

---

## 各项逐项评审

### 1. PRD 功能分层

**评分：⭐⭐⭐⭐⭐ 优秀**

#### 1.1 项目定位

> 给 AI Agent 用的万年历 MCP 服务

**评审意见：** 定位清晰且精准。

- 面向 AI Agent（而非人类用户）意味着接口需要返回结构化、机器可读的数据，而非自然语言描述。现有 DateInfo schema 使用 JSON 结构化字段，与定位一致。
- 选择 MCP（Model Context Protocol）作为服务层协议，使 Agent 可以原生调用工具，无需额外适配层。✅
- "万年历"定义了数据边界（历法、节气、节假日等），避免了无限扩展的范围蔓延。✅

#### 1.2 功能分层合理性

| 梯队 | 内容 | 评审 |
|------|------|------|
| **第一梯队** | 公农历转换、节气、节假日、干支生肖星座 | ✅ 核心高频功能，AI Agent 最常需要 |
| **第二梯队** | 宜忌吉神冲煞 | ✅ 进阶功能，有市场但依赖更复杂算法 |
| **第三梯队** | 星宿八字佛道历 | ✅ 专业小众需求，正确放在最低优先级 |

**详细说明：**

- 第一梯队的选择符合"80/20 原则"：这 4 类功能覆盖了绝大多数日历类 Agent 查询场景（如"今天是农历几号"、"下周四是什么节气"、"国庆节是哪几天"）。
- 干支/生肖/星座归入第一梯队是正确的：这类数据虽然看似"娱乐性"，但在中文语境的 AI Agent 中使用频率很高（如"我是什么星座/生肖"），且 lunar-python 零成本支持，没有理由延后。
- 宜忌吉神放第二梯队合理：数据来源更复杂（需要黄历算法），且用户群体更窄，延后实现风险更低。
- 八字/佛道历放第三梯队合理：专业度高，维护成本大，优先级最低符合 MVP 策略。

**无问题。**

#### 1.3 MCP 工具清单

| 工具 | 评审 |
|------|------|
| `get_date_info` | ✅ 核心聚合接口，一次调用返回全部第一梯队数据 |
| `solar_to_lunar` | ✅ 基础转换接口，签名简洁 |
| `lunar_to_solar` | ✅ 逆向转换，含 `leap_month` 参数正确处理闰月 |
| `get_solar_terms` | ✅ 年度节气列表，适合批量查询场景 |
| `is_holiday` | ✅ 单日判断接口，语义明确 |
| `get_holidays` | ✅ 年度假期列表，适合日历展示场景 |
| `get_almanac` | ⚠️ 在 server.py 中**未实现注册**，但 PRD 中列出 |

**发现问题：**

| 严重程度 | 问题 |
|---------|------|
| **Medium** | `get_almanac` 在 server.py 骨架中未注册为 MCP 工具。按 PRD 它属于第二梯队（宜忌），如有意延迟实现，PRD 应明确标注为"第二梯队"并从第一梯队工具清单中移除；如属于 Phase 0 遗漏，需在 Phase 1 补充注册（即使是 stub）。 |
| **Minor** | 工具签名缺少 `get_date_info` 的返回类型范围说明。建议在 docstring 中明确："本接口整合第一梯队全部字段，等价于调用 solar_to_lunar + get_solar_terms + is_holiday 的合集"，帮助 Agent 选择正确工具。 |
| **Minor** | 缺少"获取当天信息"的快捷接口（如 `get_today_info()`）。大量 Agent 查询都是"今天"，每次构造今日日期再传入 `get_date_info` 略显冗余。可考虑增加或在文档中说明使用方式。 |

---

### 2. 技术选型

**评分：⭐⭐⭐⭐ 良好**

#### 2.1 底层库：lunar-python（6tail/lunar-python）1.4.8

**评审意见：✅ 推荐，是当前 Python 生态最成熟的农历库。**

| 维度 | 评估 |
|------|------|
| 功能覆盖 | Spike 报告验证：公农历转换、节气、干支、生肖、星座全部覆盖 ✅ |
| 数据精度 | 基于天文算法（非查表），精度可靠 ✅ |
| 维护状态 | GitHub 6tail/lunar-python 持续维护（2024 年仍有更新），社区活跃 ✅ |
| 中文支持 | 原生中文输出（干支名称、节气名称、生肖等），无需额外转换 ✅ |
| 闰月支持 | 支持负数月份表示闰月，`LunarMonth.isLeap()` 可判断，接口层需做转换 ✅ |

**已知限制（需在实现中注意）：**

| 限制 | 影响 | 应对 |
|------|------|------|
| `getAnimal()` 返回精细生肖（含"貉"等），非标准十二生肖 | Minor | 统一使用 `getYearShengXiao()` 返回标准十二生肖 |
| 星座名称不含"座"字（返回"水瓶"而非"水瓶座"） | Minor | 实现层拼接"座"字，或 schema 中注明 |
| 全年节气枚举 API（`getJieQiTable()`）在 spike 中未验证 | Major | Phase 1 开始前需补充验证 |
| 节假日不内置，需外部数据源 | 已知，按决策使用静态 JSON | - |

**总体结论：** lunar-python 完全满足第一梯队需求，选型正确。

#### 2.2 服务层：Python MCP server（mcp SDK 1.26.0）

**评审意见：✅ 推荐，官方 SDK，适合 Agent 调用。**

| 维度 | 评估 |
|------|------|
| 协议合规性 | mcp SDK 1.26.0 是官方 Python SDK，协议实现完整 ✅ |
| FastMCP 易用性 | 装饰器注册工具，代码简洁，类型推导自动生成 MCP schema ✅ |
| 版本锁定 | `pyproject.toml` 中 `mcp>=1.0.0` 过于宽松，建议锁定 `>=1.26.0` ⚠️ |
| 返回类型 | 当前全部返回 `str`，建议改为 Pydantic 模型以提供 schema 信息 ⚠️ |

**发现问题：**

| 严重程度 | 问题 |
|---------|------|
| **Medium** | `mcp>=1.0.0` 版本约束过于宽松，MCP SDK 1.x 版本间存在 API 变化（如 FastMCP 在 1.2+ 才稳定）。建议改为 `>=1.26.0`，与验证版本一致。 |
| **Minor** | 所有工具返回 `str` 而非具体 Pydantic 模型，客户端无法获得结构化 schema。Phase 1 实现时应改为 `-> DateInfo`、`-> LunarDate` 等，FastMCP 支持自动序列化。 |

#### 2.3 CLI：click

**评审意见：✅ 合理，标准选择。**

- click 是 Python CLI 生态的事实标准，与 FastMCP 不冲突（两者可共用同一个 Python 包）。
- 当前 CLI 只有 `today` 命令骨架，Phase 1 实现时应扩展为调用核心业务逻辑的封装，避免 CLI 和 MCP server 各自实现一遍逻辑。
- 无问题。

#### 2.4 部署：Railway

**评审意见：⚠️ 基本可行，但需注意 MCP transport 选择。**

| 维度 | 评估 |
|------|------|
| 部署简便性 | Railway 支持直接从 GitHub 部署 Python 应用，配置简单 ✅ |
| 成本 | 小流量下免费额度充足（500 小时/月），个人/demo 项目友好 ✅ |
| 持久化存储 | 静态 JSON 文件打包进仓库，不依赖外部数据库 ✅ |
| 冷启动 | Railway 无服务器部署有冷启动（~1-3s），AI Agent 调用可能有延迟 ⚠️ |

**关键风险：MCP server transport 选择**

MCP server 有两种运行模式：

1. **stdio transport（本地进程）：** Claude Desktop、本地 Agent 直接 `subprocess` 调用，无需网络。Railway 部署无意义。
2. **HTTP/SSE transport（远程服务）：** 通过网络暴露 MCP 端点，Railway 部署才有价值。

**需要明确的问题：** PRD 未说明目标 transport 模式。如果是给 Claude Desktop / 本地 Agent 用，Railway 部署意义不大（应打包成本地可执行文件）；如果是给远程 Agent（如 API 调用方）用，需要确认使用 SSE endpoint 或 Streamable HTTP（mcp SDK 1.26.0 支持）。

**发现问题：**

| 严重程度 | 问题 |
|---------|------|
| **Major** | PRD 未明确 MCP transport 模式（stdio vs HTTP/SSE vs Streamable HTTP）。这决定了 Railway 部署的意义和实现方式。Phase 1 开始前需明确：目标客户端是本地 Agent 还是远程 API 调用方？ |
| **Medium** | Railway 的 ephemeral 文件系统（每次 deploy 重置）与静态 JSON 文件方案兼容，但 Railway 若使用 sleep 机制（免费计划），首次冷启动会有延迟，需在 Agent 调用侧做超时重试处理。 |
| **Minor** | 未规划 Railway 环境变量管理方案（如未来需要接入第三方假期 API token 时）。建议 Phase 1 建立 `.env.example` 文件作为约定。 |

#### 2.5 包管理：uv

**评审意见：✅ 优秀选择。**

- uv 是当前 Python 生态最快的包管理器，`uv.lock` 保证可复现构建。
- Railway 支持 uv（通过 `uv sync` 安装依赖）。
- 无问题。

---

### 3. 接口设计（DateInfo schema）

**评分：⭐⭐⭐ 中等，有可改进点**

#### 3.1 schema 字段完整性评审

```json
{
  "solar": "2025-01-29",                    ✅ 清晰
  "lunar": {
    "year": 2025, "month": 1, "day": 1,    ✅ 结构合理
    "leap": false,                          ✅ 闰月标识
    "label": "正月初一"                      ⚠️ 未文档化（是简写还是全称？）
  },
  "ganzhi": {
    "year": "乙巳", "month": "丁丑", "day": "甲子"   ✅ 覆盖年月日
  },
  "zodiac": "蛇",                           ⚠️ 命名歧义（应为"生肖"而非"星座"）
  "constellation": "水瓶座",               ✅ 清晰
  "solar_term": "大寒",                    ✅ 正确（当天无节气时应为 null）
  "festivals": ["春节"],                   ⚠️ 与 holiday_name 语义重叠，需区分
  "weekday": 3,                            ⚠️ 编码未定义（0-6 还是 1-7？）
  "week_of_year": 5,                       ⚠️ ISO week 还是自然周？未说明
  "is_holiday": true,                      ✅ 清晰
  "holiday_name": "春节"                   ✅ 清晰
}
```

**发现问题：**

| 严重程度 | 问题 | 建议 |
|---------|------|------|
| **Major** | **`is_workday` 字段缺失。** `holidays_2025.json` 中存在 `type: "workday"`（调休补班日），这类日期 `is_holiday=False` 但也不是普通工作日，`is_holiday` 字段无法区分，导致接口语义不完整。 | 增加 `is_workday: bool = False`（调班日为 True） |
| **Medium** | `zodiac` 字段命名歧义。在英文语境中 zodiac 既可指西方星座（constellation），也可指东方生肖（shengxiao）。与 `constellation` 字段并列时极易混淆 AI Agent 的理解。 | 改名为 `shengxiao`，或增加 `Field(description="生肖，如'龙'")` |
| **Medium** | `weekday: int` 编码标准未定义。Python `date.weekday()` 返回 0=周一，但 ISO 标准 1=周一，Agent 可能无法正确解析。 | 在 schema 注释中明确：`0=周一, 6=周日`（Python 标准）或改用字符串枚举 |
| **Medium** | `LunarDate.label` 字段含义未文档化。从 spike 报告看，`getSolar().__str__()` 返回 `"2024-02-10"`，农历全称应来自 `lunar.__str__()`（`"二〇二四年正月初一"`）。实现侧需确认 label 是简写（"正月初一"）还是全称（"二〇二四年正月初一"）。 | 在 schema 中加 `Field(description="农历中文简写，如'正月初一'（不含年份）")` |
| **Minor** | `festivals` 和 `holiday_name` 语义重叠但未区分。前者应指"传统节日名称列表"（算法来源：lunar-python），后者应指"官方假期名称"（数据来源：静态 JSON）。两者可能同时有值（春节既是传统节日，也是官方假期）。 | 在 schema 注释中区分："festivals = 传统节日，来自农历算法；holiday_name = 官方法定假期，来自节假日数据" |
| **Minor** | `week_of_year: int` 未说明是 ISO 8601 周（周一为一周开始）还是自然周。 | 注明：`ISO 8601 week number` 或加注释 |
| **Minor** | `solar_term` 字段名称在任务中的 schema 示例显示 `"solar_term": "大寒"`，但 2025-01-29 的实际节气应为无（大寒是 1 月 20 日），示例数据有误。不影响设计，但建议修正示例。 | 示例中将 `solar_term` 改为 `null` 或选择节气当天作为示例 |

#### 3.2 schema 整体结构评审

- **嵌套结构合理：** `lunar` 和 `ganzhi` 使用嵌套对象正确，避免了字段平铺导致的命名冲突。✅
- **Optional 处理合理：** `solar_term`、`holiday_name` 使用 `Optional[str] = None` 正确，只在有值时填充。✅
- **festivals 类型合理：** `List[str]` 正确，一个日期可能同时是多个节日（如中秋+国庆）。✅
- **缺少 timestamp 字段：** 考虑 AI Agent 可能需要知道精确的节气时刻（如"春分精确到几点几分"），当前 schema 只有日期精度。这是合理的 MVP 边界，第二梯队可以扩展，不作为当前问题。

---

### 4. 节假日静态 JSON 方案可维护性评估

**评分：⭐⭐⭐ 中等，决策可接受但需配套治理机制**

**优点：**
- 无外部依赖，离线可用，部署简单 ✅
- 数据来源权威（国务院通知），准确性高 ✅
- 格式清晰，人工维护门槛低 ✅
- 包含调休工作日（`type: "workday"`），语义完整 ✅

**风险评估：**

| 风险 | 严重程度 | 说明 |
|------|---------|------|
| **多年数据缺失** | Major | 当前仅有 `holidays_2025.json`，历史年份（如 2024、2023）和未来年份均无数据，`is_holiday` 和 `get_holidays` 对非 2025 年调用会返回空/错误 |
| **年度更新依赖人工** | Medium | 每年 11-12 月国务院发布下一年节假日安排，需人工添加 JSON 文件。若遗漏更新，下一年数据将缺失 |
| **数据格式无 schema 约束** | Minor | 无 JSON schema 文件，格式错误无法在 CI 中自动检测 |
| **历史数据准确性无法保证** | Minor | 若未来需补充历史年份数据，验证准确性的成本较高 |

**建议（配套治理机制）：**

1. **短期（Phase 1 内）：** 补充 2024、2026 年数据，并在 `get_holidays(year)` 实现中，当找不到对应年份 JSON 时返回明确错误（如 `{"error": "holiday data not available for year {year}", "available_years": [2025]}`），而非静默返回空。
2. **中期（Phase 2）：** 添加 GitHub Actions 定时任务（每年 12 月），提醒维护者更新下一年数据（创建 GitHub Issue）。
3. **长期（可选）：** 对接公开假期 API（如 `timor.tools/holiday-cn`）作为兜底数据源，当 JSON 缺失时 fallback 到 API。

**总体结论：** 静态 JSON 方案对于 MVP 阶段是合理选择，风险可控，但需配套年度更新流程和缺失数据的错误处理机制。

---

### 5. Railway 部署风险（补充）

见第 2.4 节"部署：Railway"的详细评审。

核心结论：Railway 部署技术上可行，**但 PRD 必须先明确 MCP transport 模式**（这是 Phase 1 架构决策，不能延后）。

---

## 发现问题汇总

### 🔴 Blocking（但不阻塞 Phase 1 启动，需在实现过程中解决）

本次 Phase -1 review 无 blocking 问题。方案设计层面未发现需要推翻重来的决策。

### 🟡 Major（Phase 1 实现前需明确）

| # | 分类 | 问题 |
|---|------|------|
| M-1 | PRD / 部署 | MCP transport 模式未明确（stdio vs HTTP/SSE），决定 Railway 部署的实现方式 |
| M-2 | Schema | `is_workday` 字段缺失，调休上班日无法区分 |
| M-3 | 数据 | 节假日数据仅覆盖 2025 年，多年查询无数据来源，需在实现时处理缺失数据的错误返回 |
| M-4 | 技术选型 | `get_solar_terms(year)` 全年 24 节气枚举 API 在 spike 中未验证 |

### 🟠 Medium（Phase 1 内解决）

| # | 分类 | 问题 |
|---|------|------|
| Me-1 | Schema | `zodiac` 命名歧义，建议改为 `shengxiao` |
| Me-2 | Schema | `weekday` 编码标准未明确 |
| Me-3 | Schema | `LunarDate.label` 字段含义未文档化 |
| Me-4 | PRD | `get_almanac` 工具在 server.py 中未注册，需明确是第二梯队（延后）还是遗漏 |
| Me-5 | 技术选型 | `mcp>=1.0.0` 版本约束过于宽松，建议改为 `>=1.26.0` |
| Me-6 | 技术选型 | MCP 工具返回类型全为 `str`，建议改为 Pydantic 模型 |
| Me-7 | 部署 | Railway 冷启动延迟需在 Agent 调用侧做超时重试处理 |

### 🟢 Minor（建议但不阻塞）

| # | 分类 | 问题 |
|---|------|------|
| Mi-1 | Schema | `festivals` 与 `holiday_name` 语义未区分 |
| Mi-2 | Schema | `week_of_year` 未说明 ISO 标准 |
| Mi-3 | Schema | PRD 示例中 `solar_term: "大寒"` 与日期 `2025-01-29` 不符（大寒是 1 月 20 日） |
| Mi-4 | 数据 | 缺少 JSON schema 文件，格式错误无法自动检测 |
| Mi-5 | 部署 | 未规划 `.env.example` 文件约定环境变量管理 |
| Mi-6 | 技术选型 | lunar-python 星座返回值不含"座"字，实现时需拼接 |

---

## 建议（Phase 1 启动 Checklist）

**Phase 1 开始前必须明确（Major 决策）：**

- [ ] **明确 MCP transport 模式：** stdio（本地）还是 HTTP/SSE（Railway 远程）？影响 server.py 入口实现
- [ ] **补充 spike：** 验证 `get_solar_terms(year)` 全年 24 节气枚举 API（`getJieQiTable()` 或等价方式）
- [ ] **Schema 修订：** 增加 `is_workday: bool` 字段，`zodiac` 改名为 `shengxiao`，各字段加注释

**Phase 1 实现过程中修复（Medium）：**

- [ ] `is_holiday(date)` 实现时，对缺失年份返回明确错误而非静默空值
- [ ] `mcp` 版本约束改为 `>=1.26.0`
- [ ] 明确 `get_almanac` 是否纳入 Phase 1，并在 PRD 或 server.py 中标注
- [ ] MCP 工具返回类型改为 Pydantic 模型

**Phase 1 后建议（运维）：**

- [ ] 建立年度节假日数据更新 SOP（每年 12 月触发）
- [ ] 考虑补充 2024、2026 年节假日数据

---

## 总结

Phase -1 方案整体质量良好，核心技术决策（lunar-python 选型、MCP 服务层、静态 JSON 节假日、Railway 部署）均有合理依据，可以为后续开发提供正式背书。

**最重要的一个待决策项：** MCP transport 模式（stdio vs HTTP/SSE）。这是架构级决策，影响 Railway 部署的实现方式，必须在 Phase 1 第一个任务开始前明确。

在上述问题修复后，Phase 1 可安全推进。
