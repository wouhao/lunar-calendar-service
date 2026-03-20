# AGENTS.md — Lunar Calendar Service

## 最高原则
**实事求是，禁止编造。** 没有真实结果前不允许编造进展或结论。

## 角色分工
- **Codex = Coder**：执行，出方案 / 写代码 / 跑测试
- **Claude Code = Reviewer**：审查，方案 review / 代码 review
- **同一任务的 Coder 和 Reviewer 必须是不同 subagent**

## 工作流
1. PM subagent 通过 sessions_send 发任务包
2. 任务包包含：intent / goal / non_goals / scope / acceptance / 原始材料
3. 完成后通过 announce 把结果推回 PM
4. PM 更新飞书执行表，推进下一个 subtask

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
