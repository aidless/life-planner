# API Reference — 34 端点

所有端点使用统一响应格式：

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": null
}
```

错误响应（HTTP 4xx / 5xx）：

```json
{
  "success": false,
  "data": null,
  "error": "用户不存在",
  "meta": null
}
```

完整 OpenAPI 文档：http://localhost:8000/docs

## 1. Auth（认证）— 3 端点

### POST /api/auth/register

注册新用户。

**请求**：
```json
{
  "username": "demo_user",
  "email": "demo@example.com",
  "password": "DemoPass123"
}
```

**响应**（200）：
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "user": { "id": 1, "username": "demo_user", ... }
  }
}
```

**错误**：409（用户名已存在）/ 422（验证失败）

### POST /api/auth/login

登录。

**请求**：
```json
{
  "username": "demo_user",
  "password": "DemoPass123"
}
```

**响应**：同 register。

**错误**：401（用户名或密码错）。

### GET /api/auth/me

获取当前用户信息（需 Authorization header）。

**响应**：
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "demo_user",
    "email": "demo@example.com",
    "is_active": true,
    "created_at": "2026-07-17T08:26:01"
  }
}
```

## 2. College（高考志愿）— 7 端点

### POST /api/college/predict

智能推荐志愿（基于分数 + 省份 + 选科）。

**请求**：
```json
{
  "score": 587,
  "province": "山东",
  "subject_combination": "综合",
  "year": 2025
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "user_rank": 12500,
    "dash": [...],     // 冲一冲
    "steady": [...],   // 稳一稳
    "safe": [...]      // 保一保
  }
}
```

### GET /api/college/rank

查询一分一段表（某省某年某分数对应的位次）。

**查询参数**：`province` (必填), `score` (必填), `year` (可选)

### GET /api/college/scores

查询某大学某年的录取分数线。

**查询参数**：`college_id` (必填), `year` (可选)

### GET /api/college/colleges

列出所有大学（分页）。

**查询参数**：`page` (默认 1), `page_size` (默认 20), `province` (可选), `type` (可选)

### GET /api/college/colleges/{id}

获取大学详情。

**错误**：404（大学不存在）。

### POST /api/college/export-pdf

导出志愿表 PDF。

**请求**：`{"recommendation_id": 123}`

### GET /api/college/recommendations

获取当前用户的推荐历史。

## 3. DailyTracker（日常记录）— 5 端点

### POST /api/daily/logs

记录每日活动。

**请求**：
```json
{
  "date": "2026-07-17",
  "activity_type": "study",
  "description": "复习数学",
  "duration_minutes": 90,
  "mood_level": 8
}
```

### GET /api/daily/logs

查询历史（分页）。

**查询参数**：`page`, `page_size`, `start_date`, `end_date`

### POST /api/daily/logs/{id}/feedback

获取 AI 对该日志的反馈。

### GET /api/daily/stats

统计（按月聚合）。

### GET /api/daily/streak

连续记录天数。

## 4. ExamAnalyzer（考试分析）— 5 端点

### POST /api/exam/upload

上传试卷图片 + OCR 解析。

### GET /api/exams

列出当前用户的所有考试。

### GET /api/exam/{id}

获取考试详情（含每题答案）。

### POST /api/exam/{id}/analyze

AI 错题诊断。

### GET /api/exam/{id}/diagnosis

获取诊断报告。

## 5. LifePlanner（人生目标）— 5 端点

### POST /api/goals

创建长期目标。

**请求**：
```json
{
  "title": "2027 年完成研究生学位",
  "category": "education",
  "priority": 1,
  "target_date": "2027-06-30"
}
```

### GET /api/goals

列出目标（支持 `status_filter`）。

### GET /api/goals/{id}

获取目标详情。

### PUT /api/goals/{id}

更新目标（含进度）。

### DELETE /api/goals/{id}

删除目标。

## 6. AICoach（AI 教练）— 1 端点

### POST /api/ai/chat

与 Claude 对话。

**请求**：
```json
{
  "message": "我现在很迷茫，不知道该不该考研",
  "context": { "user_age": 22 }
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "reply": "我理解你的迷茫...",
    "suggestions": ["..."]
  }
}
```

**错误**：503（未配置 ANTHROPIC_API_KEY）/ 401（未登录）。

## 其他

### GET /api/health

健康检查（公开）。

**响应**：
```json
{
  "success": true,
  "data": { "status": "healthy", "version": "0.9.0" }
}
```

## 认证

除 `/api/health` 外，所有端点需要 JWT token：

```
Authorization: Bearer eyJhbGc...
```

## 限流

- 100 req / 60s / IP（内存实现）
- 超出返回 429

## 错误码

| 状态码 | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 请求错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 冲突（如 username 重复）|
| 422 | 验证失败（Pydantic）|
| 429 | 限流 |
| 500 | 服务器错误 |
| 503 | 服务不可用（如 AI key 缺失）|