# Life Planner（人生规划助手）

> AI 驱动的人生规划助手 — 覆盖学业、职业、考试、目标 4 大核心场景。
> 基于 FastAPI + React 18 + TypeScript + Ant Design 5 + Claude API 构建。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Tests: 60/60](https://img.shields.io/badge/tests-60%2F60-brightgreen.svg)](#测试)
[![mypy: 0 errors](https://img.shields.io/badge/mypy-0%20errors-blue.svg)](./pyproject.toml)

## 核心特性

- **6 大核心模块**：仪表盘 / 日常记录 / 考试分析 / 人生目标 / 学习规划 / 高考志愿 / 职业发展 / 研究生规划 / AI 教练对话
- **94+ API 端点**：覆盖学业+职业全流程
- **AI 加持**：可选 Claude API 集成，提供智能分析与建议
- **完整测试**：60 个自动化测试，my py 严格类型检查 0 错误
- **开箱即用**：Docker Compose 一键启动

## 快速开始

### 方式一：Docker（推荐）

```bash
git clone https://github.com/aidless/life-planner.git
cd life-planner
docker compose -f deploy/docker-compose.yml up -d
```

访问：
- 前端：http://localhost:5173
- API 文档：http://localhost:8000/docs

### 方式二：本地开发

**后端**：
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端**（另开终端）：
```bash
cd frontend
npm install
npm run dev
```

**AI 功能**（可选）：
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 功能模块

| 模块 | 端点数 | 说明 |
|---|---|---|
| 仪表盘 (Dashboard) | 1 | 9 模块聚合 + 5 年总览 + AI 推荐 |
| 身份认证 (Auth) | 3 | register / login / me |
| 高考志愿 (College) | 7 | 测一测 / 推荐 / 一分一段 / 收藏 / 历史 |
| 日常记录 (DailyTracker) | 5 | 每日活动 + AI 反馈 |
| 考试分析 (ExamAnalyzer) | 5 | 上传试卷 + AI 错题诊断 |
| 人生目标 (LifePlanner) | 5 | 长期目标 + 进度追踪 |
| 职业发展 (Career) | — | 简历 + 求职规划（建设中）|
| 研究生规划 (Grad) | — | 考研目标 + 倒计时（建设中）|
| AI 教练 (AICoach) | 1 | Claude 对话 |

总计：34 路由。

## 技术栈

**后端**：Python 3.11 / FastAPI / SQLAlchemy 2.0 / SQLite / Pydantic v2 / pytest
**前端**：React 18 / TypeScript / Vite / Ant Design 5 / Zustand / Axios
**AI**：Anthropic Claude API（可选）
**部署**：Docker Compose + Vercel（前端）+ GitHub Actions CI

## 项目结构

```
life-planner/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── database.py      # SQLAlchemy sync 引擎
│   │   ├── config.py        # Pydantic Settings
│   │   ├── dependencies.py  # get_current_user 等
│   │   ├── shared/          # BaseModel / 中间件
│   │   └── modules/         # 业务模块
│   │       ├── auth/        # 认证
│   │       ├── college/     # 高考志愿
│   │       ├── daily_tracker/
│   │       ├── exam_analyzer/
│   │       ├── life_planner/
│   │       └── ai_coach/
│   ├── data_pipeline/       # 爬虫 + 数据导入（cron）
│   ├── tests/               # pytest 测试
│   └── requirements.txt
├── frontend/                # React 前端
│   ├── src/
│   │   ├── pages/           # 14 个页面
│   │   ├── components/      # 共享组件
│   │   ├── store/           # Zustand 状态
│   │   ├── api/             # Axios 客户端
│   │   └── types/           # TypeScript 类型
│   ├── package.json
│   └── vite.config.ts
├── deploy/                  # Docker 部署
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── docs/                    # 文档
│   ├── getting-started.md
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── data/                    # 数据 + sqlite
│   └── life_planner.db
├── pyproject.toml           # mypy + flake8 + pytest 配置
├── .github/workflows/ci.yml # GitHub Actions
├── LICENSE                  # MIT
├── CHANGELOG.md             # 版本历史
└── CONTRIBUTING.md          # 贡献指南
```

## 测试

```bash
cd backend
$PY -m pytest tests/ -v     # 60 个测试，5 秒跑完
```

**当前状态**：60/60 通过 + 3 次连跑稳定 + mypy 0 errors in 111 source files。

## 文档

- [docs/getting-started.md](./docs/getting-started.md) — 详细安装步骤
- [docs/architecture.md](./docs/architecture.md) — 架构设计 + 数据库
- [docs/api.md](./docs/api.md) — 34 端点参考
- [docs/deployment.md](./docs/deployment.md) — 部署到阿里云 ECS / Vercel

## 路线图

- **v0.9（当前）**：6 核心模块 MVP 完成
- **v1.0（2026 Q4）**：补 C/D（健康/财务/习惯/心理/家庭/兴趣/社交/学习 8 子域）
- **v2.0（2027）**：移动端 + 国际化

## 贡献

参考 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## License

[MIT](./LICENSE) — 自由使用、修改、商用。