# lunar-calendar-service

> 给 AI Agent 使用的万年历 MCP 服务，提供公历/农历转换、节气、节假日、干支、生肖等查询能力。

## 开始之前

**如果你是 AI Agent / Coding subagent，请先读：**
- `AGENTS.md` — 角色分工、通信链路、工作规范
- `CLAUDE.md` — 技术栈、运行方式、关键决策
- `docs/PRD.md` — 完整产品需求文档

## 项目定位

为 AI Agent 提供万年历数据查询，通过 MCP（stdio）或 CLI 调用。

## 技术栈

| 层次 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 包管理 | uv |
| 底层库 | lunar-python 1.4.8 |
| 服务层 | MCP server（stdio transport） |
| Schema | Pydantic v2 |
| 节假日数据 | 静态 JSON |

## 快速开始

```bash
# 安装依赖
uv sync

# MCP server
uv run python server.py

# CLI 查询今天
uv run python cli.py today

# 运行测试
uv run pytest tests/
```

## MCP 工具

| 工具 | 说明 |
|------|------|
| `get_date_info` | 输入日期，返回完整信息 |
| `solar_to_lunar` | 公历转农历 |
| `lunar_to_solar` | 农历转公历 |
| `get_solar_terms` | 全年二十四节气 |
| `get_holidays` | 全年法定节假日 |
| `is_holiday` | 某天是否放假/调休 |

## 目录结构

```
├── AGENTS.md              # 角色分工与工作规范
├── CLAUDE.md              # 技术栈与运行方式
├── README.md              # 本文件
├── server.py              # MCP server 入口
├── cli.py                 # CLI 入口
├── services/
│   └── date_service.py    # 业务逻辑层
├── models/
│   └── date_info.py       # Pydantic schema
├── data/
│   └── holidays_2025.json # 节假日静态数据
├── docs/
│   ├── PRD.md             # 产品需求文档
│   └── *.review.*.md      # Review 产物
├── spike/                 # 技术验证
└── tests/                 # pytest 用例
```

## 路线图

- [x] Phase -1：方案确认
- [x] Phase 0：项目骨架搭建
- [ ] Phase 1：核心功能（第一梯队）
- [ ] Phase 2：黄历增强（第二梯队）
- [ ] Phase 3：高级功能（第三梯队）

## License

MIT
