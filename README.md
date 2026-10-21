# Life Planner（人生规划助手）

> AI 驱动的人生规划助手 — 覆盖学业、职业、考试、目标 4 大核心场景。
> 基于 FastAPI + React 18 + TypeScript + Ant Design 5 + Claude API 构建。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Tests: 82](https://img.shields.io/badge/tests-82-brightgreen.svg)](#测试)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## 核心特性

- **9 大模块**：仪表盘 / 日常记录 / 考试分析 / 人生目标 / 高考志愿 / 职业发展 / AI 教练 / 智能推荐 / 身份认证
- **33 个 API 端点**：覆盖学业+职业全流程
- **AI 加持**：可选 Claude API 集成，无 key 时自动降级为本地确定性统计 + 模板反馈
- **完整测试**：82 个自动化测试（pytest）+ 18 个活体测试默认 skip
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
| AI 教练 (AICoach) | 3 | 对话 / 分析 / 模块列表 |
| 智能推荐 (Recommend) | 3 | 规则引擎冲稳保推荐 |

总计：33 个 API 路径（9 个业务域）。

> **立意收缩（2026-09）**：愿景层 11 域（财务/习惯/健康/心理/家庭/兴趣/社交/学习/旅行/亲密/意义）与研究生规划已软归档（代码在 `backend/app/modules_archive/` 与 `frontend/src/pages_archive/`，可回滚）。当前聚焦 4 场景 + AI + 数据积累两根承重柱。

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
│   │   ├── pages/           # 13 个业务页面（+ 登录/注册）
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
$PY -m pytest tests/ -v     # 82 个测试，6 秒跑完
```

**当前状态**：82 通过 + 18 活体 skip，3 次连跑稳定。

**数据积累现状**（`scripts/import_json_scores.py` 实测入库，幂等可复算）：`college_scores` 50,865 行、`province_ranks` 550 行（山东 2025 一分一段），覆盖山东 2024/2025 + 广东 2024/2025。

## 文档

- [docs/getting-started.md](./docs/getting-started.md) — 详细安装步骤
- [docs/architecture.md](./docs/architecture.md) — 架构设计 + 数据库
- [docs/api.md](./docs/api.md) — 33 端点参考
- [docs/deployment.md](./docs/deployment.md) — 部署到阿里云 ECS / Vercel

## 路线图

- **v0.9（当前）**：立意收缩——聚焦 4 场景 + AI 规则降级 + 数据入库（分数线 50,865 + 位次 550）
- **v1.0（2026 Q4）**：AI 深度分析（接 Claude）+ 「越用越准」长期数据积累闭环
- **v2.0（2027）**：移动端 + 国际化；愿景层域（健康/财务/习惯等）按需回滚启用

## 贡献

参考 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## License

[MIT](./LICENSE) — 自由使用、修改、商用。