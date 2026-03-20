# PRD: 万年历服务 (Lunar Calendar Service)

## 项目名称
万年历 / Lunar Calendar Service

## 定位
一个给 AI Agent 使用的万年历服务，通过 MCP 或 CLI 被其他 AI 请求。

## GitHub 仓库
新建：wouhao/lunar-calendar-service

## 核心功能

### 第一梯队（必做）
- 公历 ↔ 农历转换
- 二十四节气（查某天节气 / 下一个节气）
- 中国传统节日（春节、中秋、端午、清明、重阳等）
- 法定节假日 / 调休
- 星期几 / 第几周
- 干支纪年（年/月/日干支）
- 生肖
- 星座

### 第二梯队（建议做）
- 每日宜忌
- 吉神方位（喜神/福神/财神）
- 冲煞
- 纳音
- 彭祖百忌

### 第三梯队（可选）
- 星宿、八字、五行
- 胎神方位
- 佛历 / 道历
- 黄道吉日查询

## 接口形态
### MCP 服务（主推）
- get_date_info：输入日期，返回完整信息
- solar_to_lunar：公历转农历
- lunar_to_solar：农历转公历
- get_holidays：全年法定节假日
- get_solar_terms：全年二十四节气
- is_holiday：某天是否放假/调休
- get_almanac：宜忌/吉神/冲煞等黄历信息

### CLI（附带）
本地命令行查询。

## 技术方案
- 底层库：lunar-python（6tail/lunar-python）
- 服务层：Python MCP server
- 部署：云端（Railway / Fly.io 等轻量平台）

## 里程碑
- Phase -1 方案：确认 PRD、技术选型、接口设计
- Phase 0 计划：拆分子任务、排优先级
- Phase 1 核心功能：第一梯队 + MCP server
- Phase 2 黄历增强：第二梯队
- Phase 3 高级功能：第三梯队
