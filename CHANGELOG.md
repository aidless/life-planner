# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — v1.0 路线图

### Planned (优先级 P0 → P2)
- 健康子域（health_logs + exercise_records + 步数睡眠 BMI）
- 财务子域（transactions + budgets + goals）
- 习惯子域（habits + checkin + streak）
- 心理/家庭/兴趣/社交/学习 5 个 P1 子域
- 旅行/亲密/意义 3 个 P2 子域
- 12 维度 Dashboard 替换当前 9 模块布局
- 5 年人生总览组件

## [0.9.0] - 2026-07-17 — MVP 完成

### Added
- 后端：6 大核心模块（auth / college / daily_tracker / exam_analyzer / life_planner / ai_coach）
- 34 API 路由（FastAPI）
- 前端：14 个页面（React 18 + TypeScript + Ant Design 5）
- 60 个 pytest 测试（连续 3 次连跑稳定）
- mypy 严格类型检查：0 errors in 111 source files
- Pydantic v1 → v2 迁移（4 schema 文件）
- GitHub Actions CI（mypy + pytest + flake8）
- Docker Compose 多服务部署配置
- 51k+ college_scores + 2.5k college_info 数据
- bcrypt 4.x 锁定（兼容 passlib 1.7.4）
- 数据库 schema 修复（users 表与 User model 一致）
- college services 字段名修复（Bug 12）
- 测试 fixture 隔离稳定（Bug 14）

### Changed
- 移除 legacy 双轨制（backend/routers/ + backend/services/）
- 统一 API response envelope `{success, data, error, meta}`
- 速率限制中间件统一响应格式

### Fixed
- Bug 1：bcrypt 5.0 + passlib 1.7.4 兼容性
- Bug 2：college 模块缺失（W27 重建）
- Bug 3：双 Base 问题
- Bug 4-6：Column[str] 直接赋值（3 处）
- Bug 7：Pydantic v1 配置类
- Bug 8：crawl_shandong_ranks 虚构引用
- Bug 9：CollegeRecommendation 字段名错
- Bug 10：PredictRequest 输入验证缺失
- Bug 11：RateLimit envelope 不一致
- Bug 12：CollegeInfo 字段名 `college_name` → `name`（W31）
- Bug 13：users 表 schema 与 User model 不一致（W31）
- Bug 14：测试间 DB state 污染（W31 修 Bug 13 时连带修复）

## [0.5.0] - 2026-06 — 早期开发

### Added
- 初始 FastAPI 后端 + React 前端
- 高考志愿数据爬虫（山东 / 河南 / 广东）
- 基础认证 + JWT

[Unreleased]: https://github.com/aidless/life-planner/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/aidless/life-planner/releases/tag/v0.9.0
[0.5.0]: https://github.com/aidless/life-planner/releases/tag/v0.5.0