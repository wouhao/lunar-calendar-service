# lunar-calendar-service

> 万年历 API 服务 —— 提供阴历/阳历转换、节气、节假日、黄历宜忌等数据查询能力。

## 项目定位

`lunar-calendar-service` 是一个轻量级的万年历后端服务，目标是：

- 提供 **阴历 ↔ 阳历** 互转接口
- 查询 **二十四节气**（精确到时刻）
- 查询 **中国法定节假日 / 调班日**
- 查询 **黄历宜忌、干支、生肖**
- 以 REST API 形式对外暴露，方便前端和第三方集成

## 目录结构

```
lunar-calendar-service/
├── README.md           # 项目说明
├── docs/               # 设计文档、API 规范
├── src/                # 核心业务代码（待实现）
├── tests/              # 单元 / 集成测试
└── scripts/            # 工具脚本（部署、数据生成等）
```

## 技术选型（规划中）

| 层次 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| Web 框架 | FastAPI |
| 阴历算法 | lunardate / lunarcalendar |
| 部署 | Docker + 云函数（待定） |

## 快速开始

> ⚠️ 项目初始化阶段，业务代码尚未实现。

```bash
git clone https://github.com/wouhao/lunar-calendar-service.git
cd lunar-calendar-service
```

## 路线图

- [ ] Phase 0：项目骨架搭建
- [ ] Phase 1：阴历/阳历转换核心算法
- [ ] Phase 2：节气数据接口
- [ ] Phase 3：节假日数据接口
- [ ] Phase 4：黄历宜忌接口
- [ ] Phase 5：API 文档 & 部署

## 贡献

欢迎 Issue 和 PR。

## License

MIT
