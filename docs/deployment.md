# Deployment — 部署到生产环境

## 方案一：阿里云 ECS（推荐国内）

### 1. 准备服务器

```bash
# 在 ECS 上安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 上传代码

```bash
# 本地
scp -r life-planner/ root@<your-server-ip>:/opt/
```

### 3. 配置环境变量

```bash
cd /opt/life-planner
cat > .env <<EOF
# Backend
SECRET_KEY=$(openssl rand -hex 32)
ANTHROPIC_API_KEY=sk-ant-...

# Database (PostgreSQL)
POSTGRES_USER=life_planner
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=life_planner

# Frontend
VITE_API_URL=https://api.your-domain.com
EOF
```

### 4. 启动

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.prod.yml up -d
```

### 5. 配置 Nginx + SSL

```nginx
# /etc/nginx/sites-available/life-planner
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 前端
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 6. 备份数据库

```bash
# 每天凌晨 3 点备份
cat > /etc/cron.daily/life-planner-backup <<EOF
#!/bin/bash
docker exec life-planner-db pg_dump -U life_planner life_planner | gzip > /backup/life-planner-\$(date +\%Y\%m\%d).sql.gz
# 保留 30 天
find /backup -name "life-planner-*.sql.gz" -mtime +30 -delete
EOF
chmod +x /etc/cron.daily/life-planner-backup
```

## 方案二：Vercel + Railway

适合不想运维服务器的场景。

### 1. 前端 → Vercel

```bash
cd frontend
npm i -g vercel
vercel login
vercel --prod
```

设置环境变量：
- `VITE_API_URL` = `https://api.railway.app`

### 2. 后端 → Railway

1. 访问 https://railway.app
2. 新建项目 → Deploy from GitHub
3. 选择仓库 + backend 目录
4. 设置环境变量（SECRET_KEY + ANTHROPIC_API_KEY）
5. 部署

### 3. 数据库

Railway 提供 PostgreSQL 插件，直接添加即可。

## 方案三：自托管 Docker Swarm / Kubernetes

适合大规模生产环境。

参考 `deploy/k8s/`（未来提供）。

## GitHub Actions 自动部署

`.github/workflows/ci.yml` 已配置：

- **PR**：自动跑 mypy + pytest + flake8
- **main 分支 push**：构建 Docker 镜像推送到 GitHub Container Registry
- **手动触发**：部署到测试 / 生产

## 监控

### 健康检查

```bash
curl https://api.your-domain.com/api/health
```

### 日志

```bash
docker compose logs -f backend
```

### 指标（推荐加）

- **Prometheus + Grafana** — 指标采集
- **Sentry** — 异常追踪
- **UptimeRobot** — 在线监控

## 性能优化

1. **数据库索引**：常用查询字段已加索引
2. **缓存层**：Redis（未来）
3. **CDN**：Vercel 自动 + CloudFlare
4. **Gzip**：Nginx 已启用
5. **连接池**：SQLAlchemy 默认池

## 故障恢复

### 数据库备份恢复

```bash
# 恢复
gunzip -c /backup/life-planner-20260717.sql.gz | docker exec -i life-planner-db psql -U life_planner life_planner
```

### 回滚

```bash
# 保留最近 3 个镜像
docker image prune -a --filter "until=72h"
docker compose up -d  # 用 image: tag 回滚
```

## 域名 + DNS

1. 在阿里云 / Cloudflare 购买域名
2. 添加 A 记录：`@` → ECS IP
3. 添加 CNAME：`api` → 后端域名
4. 等待 DNS 传播（5-30 分钟）

## SSL 证书

免费 Let's Encrypt：

```bash
sudo certbot certonly --nginx -d your-domain.com
sudo certbot renew --dry-run  # 测试自动续期
```

## 下一步

- 监控 + 告警（Prometheus + Alertmanager）
- 日志聚合（ELK）
- 多区域部署