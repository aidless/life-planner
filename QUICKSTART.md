# Life Planner - 快速启动指南

## 方式一：Docker Compose（推荐）

```bash
cd deploy
docker compose up -d --build
```

访问：http://localhost:5173 （前端）· http://localhost:8000/docs （API 文档）

默认使用 SQLite，数据在 `backend_data` 卷里；不需要外部 Postgres。生产部署用 `docker-compose.prod.yml`，并必须先设置 `SECRET_KEY`。

---

## 方式二：本地启动（开发）

### 后端
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

---

## 环境变量配置

复制 `deploy/.env.example` 为 `deploy/.env`，并修改：
- `SECRET_KEY`：必须修改，用于 JWT 签名
- `DB_PASSWORD`：数据库密码
- `ANTHROPIC_API_KEY`：Claude API 密钥（可选）

---

## 示例数据
没有预置账号。注册任意新账号后，后端会自动注入 30 天示例数据，便于第一次打开仪表盘时看到真实结构；这些是虚构的演示记录，不是真实用户数据。
