# Life Planner - 快速启动指南

## 方式一：Docker Compose（推荐）

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
