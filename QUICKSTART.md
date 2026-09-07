# Life Planner - 快速启动指南

## 生产态访问（当前唯一入口）

线上单源拓扑：后端 4800 同时 serve API 与前端静态页。

- 访问：http://localhost:4800（注册即用；新用户自动注入 30 天示例数据）
- 健康检查：http://localhost:4800/api/health
- 决策推荐页：http://localhost:4800/recommend（P5：规则引擎实时计算，无需 AI 密钥）
- 定时推送：cron 每天 08:00 / 21:00 全用户计算推荐并写入通知箱（`crontab -l` 应见 2 条 `recommend_push.py`）
- 守护：`ops/keeper.sh` 只保活 4800（`check` 应回 `backend=up`）

> 历史备注：5173（vite dev）/ 8080 / 8001 独立 serve 已于 P3-2 退役——
> 它们没有 /api 代理，直接访问必坏。不要再从这些端口进入。

---

## 方式一：Docker Compose（开发联调用）

### 生产环境（简单启动）
```bash
cd deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

访问：http://localhost:5173

### 开发环境
```bash
cd deploy
docker-compose up -d
```

访问：http://localhost:5173 (前端 dev server)

---

## 方式二：本地启动（开发）

### 后端
```bash
cd backend
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
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

## 默认的账户
- 手机号：13800000000
- 密码：Test123456

（首次启动后需先注册）
