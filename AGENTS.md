# AGENTS.md — Lunar Calendar Service

## 最高原则
**实事求是，禁止编造。** 没有真实结果前不允许编造进展或结论。

## 角色体系（两层架构 v2）

### 用户（小主）
- 提需求、做最终拍板
- 只和 main agent 对接

### main agent（萝卜，兼 PM）
- 需求澄清、任务拆分、飞书更新
- 通过 sessions_send 调度 Codex / Claude Code
- 技术选型、方向拍板必须和用户讨论后再定

### Codex（Coder）
- 持久 session，执行编码任务
- 优先使用 `codex exec`
- 完成后通过 announce 回传 main agent

### Claude Code（Reviewer）
- 持久 session，执行 review 任务
- 优先使用 `claude` CLI
- 完成后通过 announce 回传 main agent

### 硬规则
- **同一任务的 Coder 和 Reviewer 必须是不同 subagent，严禁自审**
- **技术选型、需求决策 → main agent 和用户讨论后回传结论**

## 通信链路
```
用户 ←→ main agent ←sessions_send→ Codex / Claude Code
                    ←announce────── Codex / Claude Code
```

## 工作流
1. main agent 通过 sessions_send 发任务包
2. 任务包包含：intent / goal / non_goals / scope / acceptance / 原始材料 / 工具提醒
3. 完成后通过 announce 把结果推回 main agent
4. main agent 更新飞书执行表，推进下一个 subtask

## 仓库规范
- commit message 带 subtask ID：`feat(P1-1): implement get_date_info`
- 每个 subtask 完成后 push 到 main
- 不擅自扩大 scope，任务包要什么就做什么

## 关键文件
- PRD：`docs/PRD.md`
- 业务逻辑：`services/date_service.py`
- Schema：`models/date_info.py`
- MCP server：`server.py`
- 节假日数据：`data/holidays_YYYY.json`
