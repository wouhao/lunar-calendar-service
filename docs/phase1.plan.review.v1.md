# Phase 1 拆分方案 Review

**entity_id:** review-20260320-phase1-plan  
**parent_task_id:** task-20260320-001  
**review 日期：** 2026-03-20  
**reviewer：** Claude Code Reviewer Subagent  
**审查范围：** Phase 1 subtask 拆分方案的合理性、依赖关系、acceptance 可判断性

---

## 总体评价

Phase 1 拆分方案整体方向正确，11 个 subtask 覆盖了 Phase 1 验收所需的全部工作。**拆分粒度基本合适**，没有明显过大或过小的 subtask。各 subtask 的标题和内容也足够清晰，acceptance 可判断。

**主要问题：依赖关系存在方向性错误。** P1-2、P1-3、P1-5、P1-6 被标记为依赖 P1-1，但从架构语义上看，`get_date_info` 是聚合接口，应当依赖底层的转换函数，而非底层函数依赖聚合接口。这一倒置不影响 Codex 执行（因为可以解释为"P1-1 先建立共享逻辑层，后续各接口复用"），但会引起歧义，建议在分发任务前明确说明意图。

**次要问题：P1-9 测试依赖 P1-7 导致测试滞后**，以及 **P1-8 CLI 可与 P1-2~P1-6 并行**（当前依赖链过于保守）。

**结论：方案通过 review，可分发 Codex 执行。** 建议在分发任务时补充说明依赖的实际含义，避免歧义。下列修改项不阻塞执行，但在任务包描述中补充说明更佳。

---

## 各 subtask 逐项评审

### P1-0：全年节气 API spike

**评审：✅ 通过**

- 目的明确：验证 `get_solar_terms(year)` 实现方案，输出 spike 结论。
- 前置 spike 的设计正确。现有 `spike/lunar_test.py` 已验证公农历转换、单日节气（`getJieQi()`）和下一节气（`getNextJieQi()`），但**全年 24 节气枚举 API**（`getJieQiTable()` 或等价接口）**尚未验证**，P1-0 就是补这个空缺。
- 无依赖，可立即启动，是正确的起点。
- **acceptance 建议补充：** spike 结论应包含"可用 API 方法名 + 返回格式 + 示例输出"，不能只输出"可行/不可行"。

### P1-1：get_date_info 实现

**评审：⚠️ 通过，但依赖说明需澄清**

- `get_date_info` 是核心聚合接口，返回 `DateInfo`（含 is_workday），是 Phase 1 最重要的 subtask。
- **依赖 P1-0 合理：** `DateInfo.solar_term` 字段需要全年节气数据，而 P1-0 验证了获取节气的 API。
- **依赖方向疑问：** P1-2（solar_to_lunar）、P1-3（lunar_to_solar）、P1-5（is_holiday）、P1-6（get_holidays）都被标记为依赖 P1-1，但 `get_date_info` 在语义上应**使用**这些函数的能力，而非这些函数**依赖** `get_date_info`。

  **PM 意图推断（最合理的解释）：** P1-1 不仅实现 `get_date_info` MCP 工具，还建立**共享逻辑层**（internal helper functions：`_convert_solar_to_lunar()`、`_check_holiday()` 等），后续 P1-2~P1-6 在此共享层基础上封装成独立 MCP 工具入口。这种设计是合理的，但需要在任务包中显式说明，否则 Codex 可能只实现 `get_date_info` 而不建立共享层。

- **is_workday 覆盖确认：** 任务描述中包含"含 is_workday"，schema 中 `DateInfo.is_workday` 字段已在 commit e49d5a0 中添加。P1-1 需要实现从 `holidays_YYYY.json` 中读取调休上班日（`type: "workday"`）并填充 `is_workday=True` 的逻辑。

### P1-2：solar_to_lunar 实现

**评审：⚠️ 通过，依赖方向需澄清**

- 功能明确：公历→农历转换，返回 `LunarDate`。
- **依赖 P1-1 的语义问题：** 如按 PM 意图（P1-1 建立共享层），则 P1-2 在 P1-1 完成后只需封装 `_convert_solar_to_lunar()` helper 为 MCP 工具，工作量小，粒度合适。
- 如 Codex 误解为"P1-2 的逻辑依赖 P1-1 的产出"，可能导致困惑（`solar_to_lunar` 逻辑与 `get_date_info` 没有真实代码依赖关系）。
- **建议：** 任务包中注明"P1-1 已实现 `_convert_solar_to_lunar()` helper，P1-2 只需封装为 MCP tool endpoint"。

### P1-3：lunar_to_solar 实现

**评审：⚠️ 通过，闰月支持需明确验收**

- 功能明确：农历→公历转换，含闰月支持。
- 闰月支持是 lunar-python 的特性（通过负数月份或 `leap_month: bool` 参数），需要在 acceptance 中验证闰月场景。
- **acceptance 建议：** 明确验收用例，如 `lunar_to_solar(2023, 2, 1, leap_month=True)` 应返回闰二月初一对应的公历日期。
- 同 P1-2，依赖方向问题同上。

### P1-4：get_solar_terms 实现

**评审：✅ 通过**

- 功能明确：全年 24 节气列表，`get_solar_terms(year)`。
- 依赖 P1-0（spike 结论）正确，需要等 spike 确认 API 后再实现。
- **P1-0 和 P1-4 是否应合并？** 不建议合并。spike 是探索性工作，产物是"结论文档 + 验证代码"；实现是交付物代码。两者目标不同，分开便于 reviewer 评审每一步的产物质量。若合并，spike 结论无法被单独 review。
- P1-4 **不依赖 P1-1** 是正确的——全年节气列表是独立功能，不需要聚合接口。

### P1-5：is_holiday 实现

**评审：✅ 通过**

- 功能明确：判断单日是否放假/调休，含缺失年份报错。
- 缺失年份报错要求已在任务描述中明确，acceptance 可判断（返回明确报错 vs 静默返回 False）。
- **关于依赖 P1-1：** `is_holiday` 只需读取 JSON 文件，与 lunar-python 无关，技术上不依赖 P1-1 的任何逻辑。如按"共享层"设计，P1-1 可能会建立 JSON 数据加载层（`_load_holiday_data(year)`），那么 P1-5 依赖 P1-1 是合理的。需明确。
- **缺失覆盖检查：** is_workday 语义包含在 P1-5 中吗？任务描述"是否放假/调休"暗示 is_holiday（放假）和 is_workday（调休上班）应该都覆盖。建议明确：P1-5 返回的类型是 `bool`（仅 is_holiday），还是包含 `is_workday` 信息的结构体？当前 server.py 中 `is_holiday(date) -> str` 返回 str，Phase 1 是否改为结构化返回？建议在任务包中说明。

### P1-6：get_holidays 实现

**评审：✅ 通过**

- 功能明确：全年节假日列表，含缺失年份报错。
- 与 P1-5 配套，acceptance 可判断。
- 同 P1-5 的依赖 P1-1 问题。

### P1-7：MCP server stdio 集成

**评审：✅ 通过，顺序合理**

- 将 6 个占位工具改为真实实现，stdio transport。
- **放最后是否合理？合理。** 以下原因支持：
  1. 依赖全部工具实现完成（P1-2~P1-6）。
  2. server.py 已有骨架，P1-7 主要是替换 `return "not implemented"` 为真实调用，工作量不大。
  3. stdio transport 已在 `server.py` 的 `mcp.run()` 中隐式支持（FastMCP 默认 stdio），P1-7 主要是接线工作。
- **acceptance 建议补充：** P1-7 的验收应包含端到端验证——实际运行 MCP server 并通过 stdio 客户端（如 `mcp dev server.py` 或 `inspect` 命令）调用 6 个工具，确认返回真实数据而非 stub。

### P1-8：CLI today 实现

**评审：✅ 通过，可提前并行**

- 功能明确：`lunar-cal today` 输出真实日期信息。
- **依赖只有 P1-1 是合理的**——CLI today 只需调用 `get_date_info(today)` 的底层逻辑，不需要等 P1-7 MCP 集成完成。
- **并行机会：** P1-8 可与 P1-2~P1-7 并行运行（只要 P1-1 完成）。当前计划中 P1-8 没有被阻塞在 P1-7 上，是正确的。
- P1-8 的"真实日期信息"应明确输出格式（至少包含公历、农历、干支、节气），建议在任务包中给出示例输出。

### P1-9：pytest 用例补充

**评审：⚠️ 通过，但测试依赖顺序偏晚**

- 覆盖 6 个工具的基本正确性测试，依赖 P1-7。
- **测试滞后问题：** 让测试依赖 P1-7 意味着所有实现完成后才写测试，这不符合"接口先于实现"的原则，且实现 bug 可能要到最后才被发现。
- **但对于当前项目规模，可接受：** lunar-calendar-service 是个小型项目，不追求严格 TDD。将测试集中在 P1-9 便于 Codex 专注实现，再由专项任务补测试。
- **建议调整：** P1-9 可以依赖 P1-2~P1-6（不需要等 P1-7），因为测试可以直接测试业务函数，不需要通过 MCP server。这样测试可以更早写，也不依赖 MCP 集成是否完成。
- **acceptance 建议：** 明确"基本正确性测试"的最低覆盖范围，如：每个工具至少 2 个正向用例 + 1 个异常用例（如缺失年份）。

### P1-R：Phase 1 实现 review

**评审：✅ 通过**

- 依赖 P1-9（全部实现 + 测试完成后）正确。
- acceptance 明确（review 所有 P1-1~P1-9 产物）。

---

## 发现的问题与建议

### 🟡 需在任务包分发前澄清

| # | 问题 | 建议 |
|---|------|------|
| A-1 | **依赖方向语义歧义**：P1-2、P1-3、P1-5、P1-6 依赖 P1-1，但架构语义是 P1-1 聚合其他工具的能力，存在逻辑倒置 | 在 P1-1 任务包中明确：P1-1 需建立"共享逻辑层"（_helper functions），P1-2~P1-6 在此基础上封装 MCP tool endpoint |
| A-2 | **P1-5 返回类型不明确**：`is_holiday` 返回 `bool` 还是包含 `is_workday` 信息的对象？ | 明确返回类型和字段，与 DateInfo 中的 `is_holiday` / `is_workday` 语义对齐 |
| A-3 | **P1-7 acceptance 缺少端到端验证要求** | 补充：必须用 stdio 客户端实际调用 MCP server 并确认返回真实数据 |

### 🟢 建议优化（不影响执行）

| # | 问题 | 建议 |
|---|------|------|
| B-1 | P1-9 依赖 P1-7，测试滞后 | 改为依赖 P1-2~P1-6，允许测试与 MCP 集成并行 |
| B-2 | P1-0 spike 的 acceptance 过于模糊 | 明确：spike 结论需包含可用 API 方法名、返回格式、示例代码 |
| B-3 | P1-3 闰月场景无显式验收用例 | 在任务包中给出一个闰月测试用例（如 2023 年闰二月） |
| B-4 | P1-8 输出格式未定义 | 给出 `lunar-cal today` 的示例输出，至少含公历、农历、干支、节气字段 |

---

## 遗漏 subtask 检查

| 检查项 | 结论 |
|--------|------|
| is_workday 实现 | ✅ 已覆盖：P1-1 描述"含 is_workday"，P1-5 描述"是否放假/调休" |
| 缺失年份报错处理 | ✅ 已覆盖：P1-5、P1-6 均明确"含缺失年份报错" |
| get_solar_terms spike | ✅ 已有 P1-0 |
| stdio transport 集成 | ✅ P1-7 明确包含 stdio transport |
| 节假日 JSON 数据加载层 | ⚠️ 隐含在 P1-5/P1-6 中，未显式说明；如 P1-1 负责建立共享数据层，需在 P1-1 描述中明确 |
| MCP server 端到端测试 | ⚠️ P1-9 测试用例未明确是否包含 MCP 端到端验证，建议补充说明 |

---

## Phase 1 整体验收可行性

**Phase 1 验收目标：MCP server 本地可调用，6 个工具返回正确结果。**

当前拆分方案**可以支撑此验收目标**，条件是：
1. P1-7 完成后 MCP server 能通过 stdio 真实运行
2. P1-9 测试覆盖了 6 个工具的基本正确性

关键路径：`P1-0 → P1-1 → P1-2~P1-6 → P1-7 → P1-9 → P1-R`

**最长链：** P1-0 → P1-1 → P1-5/P1-6 → P1-7 → P1-9 → P1-R（共 6 步串行），所有步骤合理，无循环依赖。

---

## 总结

**Phase 1 拆分方案：通过 review。** 可分发 Codex 执行。

**主要修改建议（分发时补充说明，不需要修改方案表格）：**

1. **P1-1 任务包**中明确："P1-1 不仅实现 `get_date_info` MCP tool，还需建立供 P1-2~P1-6 复用的共享业务逻辑层（helper functions）"。
2. **P1-5 任务包**中明确：`is_holiday()` 的返回类型（bool or struct）以及如何体现 is_workday 信息。
3. **P1-7 任务包**中补充：acceptance 需包含"通过 stdio 客户端实际调用验证"。
4. **P1-0 任务包**中补充：spike 结论需包含 API 方法名 + 返回格式 + 示例代码（否则 P1-4 无法依据结论实现）。
