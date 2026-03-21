# CLAUDE.md — Lunar Calendar Service

## 项目定位
给 AI Agent 使用的万年历 MCP 服务，详见 `docs/PRD.md`。

## 技术栈
- Python 3.11+，包管理用 uv
- 底层库：lunar-python 1.4.8（6tail/lunar-python）
- 服务层：MCP server（stdio transport）
- Schema：Pydantic v2
- 数据：静态 JSON（`data/holidays_YYYY.json`）

## 运行方式
```bash
# 安装依赖
uv sync

# 运行 MCP server
uv run python server.py

# CLI 查询今天
uv run python cli.py today

# 运行测试
uv run pytest tests/
```

## 仓库结构
- `server.py` — MCP server 入口，6 个工具已集成
- `cli.py` — CLI 入口
- `services/date_service.py` — 业务逻辑层
- `models/date_info.py` — Pydantic schema（DateInfo / LunarDate / GanZhi）
- `data/` — 节假日静态数据
- `docs/` — PRD + review 产物
- `spike/` — 技术验证
- `tests/` — pytest 用例

## 关键决策
- MCP transport：stdio 优先（MVP），后续加 HTTP/SSE 上 Railway
- 节假日数据：静态 JSON，每年手动更新，缺失年份抛 ValueError
- is_workday 字段：区分调休上班日和普通工作日
- Coder/Reviewer 分离：Codex 写代码，Claude Code 做 review

## 架构
两层架构 v2：main agent 兼 PM，直接通过 sessions_send 调度 Codex（Coder）和 Claude Code（Reviewer）。详见 workspace 的 `MULTI-AGENT-FRAMEWORK-V2.md`。

## 当前进度
- Phase -1（方案）✅
- Phase 0（骨架）✅
- Phase 1（核心功能）✅
- Phase 2（黄历增强）✅
- Phase 3（高级功能）待开始
