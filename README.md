# lunar-calendar-service

> 🗓️ 给 AI Agent 使用的中文万年历 MCP 服务。提供公农历转换、二十四节气、法定节假日、黄历宜忌、八字五行等查询能力。

**线上服务：** `https://cheerful-trust-production-065e.up.railway.app/sse`

---

## 快速接入

### Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "lunar-calendar": {
      "url": "https://cheerful-trust-production-065e.up.railway.app/sse",
      "transport": "sse"
    }
  }
}
```

### Cursor / Windsurf

在 MCP 设置里添加：

```
Name: lunar-calendar
URL:  https://cheerful-trust-production-065e.up.railway.app/sse
Type: SSE
```

### 本地运行（stdio 模式）

```bash
git clone https://github.com/wouhao/lunar-calendar-service
cd lunar-calendar-service
uv sync

# Claude Desktop 本地接入
# claude_desktop_config.json:
# {
#   "mcpServers": {
#     "lunar-calendar": {
#       "command": "uv",
#       "args": ["run", "python", "server.py"],
#       "cwd": "/path/to/lunar-calendar-service"
#     }
#   }
# }
uv run python server.py
```

---

## 可用工具（9 个）

### 基础功能

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_date_info` | `date: YYYY-MM-DD` | 返回公历/农历/干支/生肖/星座/节气/节假日完整信息 |
| `solar_to_lunar` | `date: YYYY-MM-DD` | 公历 → 农历 |
| `lunar_to_solar` | `year, month, day, leap_month?` | 农历 → 公历（支持闰月） |
| `get_solar_terms` | `year: int` | 查询某年全部 24 节气日期 |
| `is_holiday` | `date: YYYY-MM-DD` | 是否节假日 / 调休上班 |
| `get_holidays` | `year: int` | 某年全部法定节假日列表 |

### 黄历

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_almanac` | `date: YYYY-MM-DD` | 每日宜忌、吉神方位（喜/福/财）、纳音、彭祖百忌 |

### 高级

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_advanced_info` | `date: YYYY-MM-DD, hour?: 0-23` | 八字、五行、星宿、胎神、佛历、道历、黄道黑道 |
| `get_lucky_days` | `start_date, end_date, purpose?` | 查询范围内的黄道吉日，可指定用途 |

---

## 使用示例

接入后，你可以这样问 Claude：

- "今天是什么日子？有没有节气？"
- "明天黄历上宜什么忌什么？"
- "2025 年春节是哪天？"
- "下个月有哪些黄道吉日适合开业？"
- "帮我查一下 2025 年全年节假日安排"
- "农历正月初一是公历几号？"

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 包管理 | uv |
| 底层历法库 | [lunar-python](https://github.com/6tail/lunar-python) 1.4.8 |
| 服务层 | FastMCP (MCP SDK) |
| Schema | Pydantic v2 |
| 节假日数据 | 静态 JSON（2025 年） |
| 部署 | Railway |

---

## 本地开发

```bash
# 安装依赖
uv sync

# 运行测试
uv run pytest tests/ -v

# CLI 快捷查询
uv run python cli.py today

# 本地 HTTP/SSE 模式
MCP_TRANSPORT=sse PORT=8000 uv run python server.py
curl http://localhost:8000/health
```

---

## 自行部署到 Railway

项目已包含 `railway.json` 和 `Procfile`：

1. Fork 本仓库
2. 在 [Railway](https://railway.app) 创建项目，导入 GitHub 仓库
3. 部署完成后，MCP endpoint 为 `https://<your-app>.up.railway.app/sse`

---

## 路线图

- [x] Phase 1：核心功能（公农历/节气/节假日）
- [x] Phase 2：黄历增强（宜忌/方位/纳音）
- [x] Phase 3：高级功能（八字/五行/吉日）
- [x] Phase 4：Railway 云端部署
- [ ] 补充 2026 年节假日数据
- [ ] 更多年份节假日支持

---

## License

MIT

---

> 如有问题或建议，欢迎提 Issue 或 PR。
