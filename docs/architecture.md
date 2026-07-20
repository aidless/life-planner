# Architecture — Life Planner 系统架构

## 总体架构

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   React 18   │ ───── │   FastAPI    │ ───── │   SQLite /   │
│  TypeScript  │ HTTP  │   (Python)   │  ORM  │  PostgreSQL  │
│  Ant Design  │       │              │       │              │
└──────────────┘       └──────────────┘       └──────────────┘
       │                      │
       │                      │
       ▼                      ▼
┌──────────────┐       ┌──────────────┐
│   Zustand    │       │  Anthropic   │
│  (state)     │       │  Claude API  │
└──────────────┘       └──────────────┘
```

## 后端架构

### 模块结构

每个业务模块在 `backend/app/modules/<name>/` 下，包含 4 个标准文件：

| 文件 | 职责 |
|---|---|
| `models.py` | SQLAlchemy ORM 模型 |
| `schemas.py` | Pydantic 请求/响应 schema |
| `services.py` | 业务逻辑（数据库操作 + AI 调用）|
| `router.py` | FastAPI 路由（HTTP 端点）|

### 当前 6 大模块

| 模块 | 端点数 | 主要功能 |
|---|---|---|
| **auth** | 3 | 注册、登录、当前用户 |
| **college** | 7 | 高考志愿推荐（51k+ 数据）|
| **daily_tracker** | 5 | 每日活动 + AI 反馈 |
| **exam_analyzer** | 5 | 上传试卷 + AI 错题诊断 |
| **life_planner** | 5 | 长期目标 + 进度追踪 |
| **ai_coach** | 1 | Claude 对话 |

总计 **34 路由**，所有端点统一响应格式：

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": null
}
```

### 中间件栈

1. **CORSMiddleware** — 跨域
2. **RateLimitMiddleware** — 内存限流（100 req / 60s / IP）

### 认证

- **JWT (HS256)** + bcrypt 密码哈希
- `get_current_user` dependency 从 Authorization header 解析

## 数据库

### 主表（13 个）

| 表名 | 用途 | 字段数 |
|---|---|---|
| `users` | 用户账户 | 11 |
| `life_goals` | 长期目标 | 12 |
| `daily_logs` | 每日记录 | 13 |
| `exams` | 考试 | 11 |
| `exam_questions` | 错题 | 9 |
| `college_scores` | 录取分数线（51k+ 行）| 12 |
| `college_info` | 大学基础信息（2.5k+ 行）| 11 |
| `province_ranks` | 一分一段表（1.1k+ 行）| 8 |
| `college_recommendations` | 志愿推荐历史 | 9 |
| `subject_assessments` | 选科测评 | 12 |
| `subject_combinations` | 选科组合 | 6 |
| `subject_recommendations` | 选科推荐 | 8 |
| `diagnosis_reports` | 诊断报告 | 9 |

### 双 Base 说明（重要）

系统历史上存在双轨制：
- **Legacy Base**（`backend/database.py` async，老 services 用）
- **New Base**（`backend/app/shared/base_model.py`，新 modules 用）

W26 修复后，`app/main.py` 启动时同时调用两个 `metadata.create_all` 确保所有表存在。

## 前端架构

### 状态管理

- **Zustand** — 轻量全局状态（auth 用户信息）
- **React Query** — 服务端数据缓存（未启用，但已配置）

### API 客户端

`frontend/src/api/client.ts` 统一 Axios 实例：
- baseURL 从环境变量读取
- 自动注入 Authorization header
- 401 自动跳转登录页

### 路由

`frontend/src/App.tsx` 配置 React Router 6，14 个页面。

### 当前 14 个页面

| 路径 | 页面 |
|---|---|
| `/` | Dashboard |
| `/login` | 登录 |
| `/register` | 注册 |
| `/subject-selection` | 选科决策 |
| `/college-advisor` | 高考志愿 |
| `/college/:id` | 大学详情 |
| `/colleges` | 大学列表 |
| `/predict` | 测一测 |
| `/scores` | 分数查询 |
| `/daily-tracker` | 日常记录 |
| `/exam-analyzer` | 考试分析 |
| `/career-advisor` | 职业发展 |
| `/grad-advisor` | 研究生规划 |
| `/study-planner` | 学习规划 |

## 测试架构

- **pytest** — 60 个测试，5 秒跑完
- **mypy** — 严格类型检查，0 errors in 111 source files
- **GitHub Actions** — 自动跑 mypy + pytest + flake8

测试文件：
- `test_smoke.py` — 11 个基础测试
- `test_college_smoke.py` — 6 个 college 模块测试
- `test_subdomain_smoke.py` — 15 个跨模块测试
- `test_integration_smoke.py` — 10 个集成测试
- `test_edge_case_smoke.py` — 18 个边缘情况测试

## AI 集成

- **Anthropic Claude API** — 可选
- 用途：高考志愿推荐、日常记录反馈、考试错题分析、AI 教练对话
- **优雅降级**：无 API key 时返回 503，不 500

## 性能特性

- **SQLAlchemy 2.0 typed ORM** — 类型安全
- **Pydantic v2** — 快速验证
- **FastAPI async** — 高并发（虽然当前大部分端点是 sync）
- **SQLite (开发) / PostgreSQL (生产)** — 灵活切换

## 安全

- **JWT** + bcrypt 4.x 密码哈希
- **CORS** 受控
- **Rate limiting** 防滥用
- **SQL 注入防护**：SQLAlchemy ORM 自动转义
- **Pydantic 验证**：所有输入字段类型 + 长度 + 范围

## 部署

参考 [deployment.md](./deployment.md)。