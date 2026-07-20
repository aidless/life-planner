# 贡献指南

感谢你考虑为 Life Planner 做出贡献！🎉

## 行为准则

请保持开放、包容、专业的态度。所有贡献者应遵守基本的社区礼仪。

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/aidless/life-planner/issues) 中搜索，确认该 bug 尚未报告
2. 创建新 issue，标题清晰（如 "Bug: /api/auth/login 返回 500"）
3. 包含：
   - 复现步骤
   - 期望行为
   - 实际行为
   - 截图或日志（如适用）
   - 环境（Python 版本 / Node 版本 / OS）

### 提交代码

1. Fork 仓库
2. 创建 feature 分支：`git checkout -b feat/my-feature`
3. 提交代码（**遵循 Conventional Commits**）：
   - `feat:` 新功能
   - `fix:` Bug 修复
   - `docs:` 仅文档改动
   - `style:` 代码风格（不影响功能）
   - `refactor:` 重构
   - `test:` 添加或修复测试
   - `chore:` 杂项（构建、CI 等）
4. 推送到你的 fork：`git push origin feat/my-feature`
5. 创建 Pull Request

## 开发规范

### 代码风格

**Python**：
- 使用 `black` 格式化（line-length=120）
- 使用 `flake8` 检查
- 使用 `mypy` 严格类型检查（`pyproject.toml` 已配置）
- Docstring 使用 Google 风格

**TypeScript / React**：
- 使用 ESLint 配置（`frontend/.eslintrc`）
- 函数组件 + Hooks
- 避免 `any`，用具体类型
- Props 接口命名 `XxxProps`

### 测试要求

**所有 PR 必须包含测试**：
- 后端：pytest 用例放在 `backend/tests/`
- 覆盖率：新代码行覆盖率 ≥ 80%

### 提交前检查清单

```bash
# 后端
cd backend
$PY -m pytest tests/ -v        # 必须 60/60 通过
$PY -m mypy --config-file ../pyproject.toml backend  # 必须 0 errors

# 前端
cd frontend
npm run lint                   # 必须 0 错误
npm run build                  # 必须构建成功
```

CI 会自动跑这些检查，未通过的 PR 不会被合并。

## 项目架构

参考 [docs/architecture.md](./docs/architecture.md)。

### 后端模块模式

每个业务模块在 `backend/app/modules/<name>/` 下：

```
<name>/
├── __init__.py
├── models.py      # SQLAlchemy ORM
├── schemas.py     # Pydantic schemas
├── services.py    # 业务逻辑
└── router.py      # FastAPI 路由
```

### 前端页面模式

每个页面在 `frontend/src/pages/<Name>/` 下：

```
<Name>/
└── index.tsx      # 页面组件
```

## 发布流程

1. 更新 `CHANGELOG.md`
2. 更新版本号（`backend/app/config.py` + `frontend/package.json`）
3. 创建 git tag：`git tag v0.9.0`
4. 推送到 GitHub：`git push --tags`
5. 创建 GitHub Release（自动从 CHANGELOG 提取）

## 联系方式

- GitHub Issues：https://github.com/aidless/life-planner/issues
- 邮件：<maintainer@example.com>

感谢你的贡献！🚀