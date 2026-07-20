# Getting Started — 5 分钟启动 Life Planner

本指南帮助你在本地启动 Life Planner，包括后端 + 前端 + 数据库。

## 前置要求

| 工具 | 版本 | 检查 |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | 2.30+ | `git --version` |
| Docker (可选) | 20+ | `docker --version` |

## 方式一：Docker Compose（推荐）

最快方式，5 分钟启动完整服务。

### 1. 克隆仓库

```bash
git clone https://github.com/aidless/life-planner.git
cd life-planner
```

### 2. 启动服务

```bash
docker compose -f deploy/docker-compose.yml up -d
```

这会启动：
- `backend` — FastAPI 后端（端口 8765）
- `frontend` — React 前端（端口 5173）
- `db` — PostgreSQL（端口 5432）
- `nginx` — 反向代理（端口 80/443）

### 3. 访问

- 前端：http://localhost:5173
- API 文档：http://localhost:8765/docs
- 健康检查：http://localhost:8765/api/health

### 4. 停止

```bash
docker compose -f deploy/docker-compose.yml down
```

## 方式二：本地开发

适合需要修改代码的场景。

### 1. 克隆 + 进入目录

```bash
git clone https://github.com/aidless/life-planner.git
cd life-planner
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

后端运行在 http://localhost:8000

API 文档：http://localhost:8000/docs

### 3. 启动前端（另开终端）

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

### 4. 配置 AI 功能（可选）

如果你想用 AI 教练功能：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

然后重启后端。

### 5. 验证安装

打开浏览器访问 http://localhost:5173 ，注册一个新账户。

## 第一个 API 调用

```bash
# 1. 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "DemoPass123"
  }'

# 2. 登录获取 token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "DemoPass123"
  }'

# 3. 获取当前用户信息
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_token>"
```

## 下一步

- [架构设计](./architecture.md)
- [API 参考](./api.md)
- [部署到生产环境](./deployment.md)
- [贡献指南](../CONTRIBUTING.md)