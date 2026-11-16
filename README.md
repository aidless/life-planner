# Life Planner（人生规划助手）

[![CI](https://github.com/aidless/life-planner/actions/workflows/ci.yml/badge.svg)](https://github.com/aidless/life-planner/actions/workflows/ci.yml)

个人全栈人生规划演示：FastAPI + React 18 + TypeScript + Ant Design 5，可选 Claude API。注册后的计划、记录、目标和仪表盘可以在没有 Claude key 的情况下跑。
它不是经过验证的建议，不是生产服务，也不是医疗、财务、心理咨询或招生录取指导。
健康、财务、习惯三个前端仍是「即将上线」；仓库里的高考分数线是离线快照，启动时不会导入。

姊妹仓：[lifeplanner](https://github.com/aidless/lifeplanner) 是同一主题下的另一个仓库（量化看板方向），不共享本仓的代码或数据库。

<!-- honesty:start -->
openapi_paths: 71
openapi_operations: 106
backend_modules: 19
tests_collected: 79
tests_passed_default: 61
tests_skipped_default: 18
coming_soon_dimensions: health,finance,habits
<!-- honesty:end -->

上面这块由 `backend/tests/test_honesty_drift.py` 对照 `app.openapi()` 和一次默认 pytest 重算。默认 pytest 会去掉 `ANTHROPIC_API_KEY` 和 `B4_INTEGRATION`。18 个跳过是 B4 集成测试，需要仓库外的 `trust-cap` 和本机 8001 端口上的后端。静态 shields「tests 60/60」「mypy 0 errors」已删除：它们不是 CI 算出来的。

## 本地核对

第一次安装需要网络。装完之后 `make check` 不调用 Claude，也不需要 key。

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
cd frontend && npm install && cd ..
make check
```

`make check` 等于 `make check-backend`（pytest + mypy `backend/app`）和 `make check-frontend`（eslint、`tsc --noEmit`、`npm run build`）。mypy 按 `pyproject.toml` 把代码当成 Python 3.11 来查，范围只有 `backend/app`，不含 `data_pipeline/`、`scripts/` 和测试。不要把某一次的 error 条数写成徽章。改这套检查之前，同一条 mypy 命令报过 7 个错误、查了 103 个文件；当时的徽章写的是 111 个文件、0 错误。

开发时后端在 `backend/` 里启动：`uvicorn app.main:app --reload --port 8000`。前端是 `frontend/` 里的 `npm run dev`（5173）。没有 key 时，AI 教练返回固定句子「AI 分析服务未配置（缺少 ANTHROPIC_API_KEY）」，不假装成功。

## CI 实际跑什么

| Workflow | 做什么 |
|---|---|
| `.github/workflows/ci.yml` `verify` | 编译已跟踪的 Python；检查 Markdown 相对链接 |
| `ci.yml` `mutation-control` | 故意写坏一个 `.py`，确认编译门会失败 |
| `ci.yml` `secret-scan` | gitleaks，全历史 |
| `ci.yml` `tests` | 安装 `backend/requirements-dev.txt`，然后 `make check-backend` |
| `ci.yml` `frontend` | `npm install`，然后 `make check-frontend` |
| `pr-checks.yml` | 只做 `compileall`，语法错误会失败。不跑测试 |
| `packaging.yml` / `publish.yml` | 只有 `pyproject.toml` 含 `[project]` 或 `[build-system]` 才打包。本仓没有这两节，所以跳过。本仓不是 PyPI 包 |
| `sast.yml` | 再跑一次 gitleaks |

`ci.yml` 的测试 job 用 Python 3.12。文档里的下限是 3.11+。CI 不跑 flake8，不构建镜像，也不部署。

## 界面里什么能进

后端 `backend/app/modules/` 下 19 个 `router.py`：auth、life_planner、daily_tracker、exam_analyzer、ai_coach、college、health、finance、habits、career、psychology、family、interest、social、learning、travel、intimacy、meaning、dashboard。另有两个应用路由 `/api/health`、`/api/info`，不算在这 19 个里。

仪表盘 12 个维度里，健康、财务、习惯的 `status` 是 `coming_soon`，没有路由。其余维度有页面。注册时会写入约 30 天随机示例（含健康、财务、习惯的行），仪表盘会标明那是示例。已开放维度的平均分不再把这三个未开放维度算进去。

## 高考数据

这些文件在仓库里，**不会**在 `create_app` 或 Compose 启动时导入。新鲜克隆的 SQLite 是空的。志愿接口在没有 `province_ranks` 行时返回空列表，不再填一个占位位次。

| 文件 | 本次清点 |
|---|---|
| `backend/data/raw/scores/shandong_2025.json` | 21381 条，`source` 为 `sdzk.cn_2025`，`year` 为 2025 |
| `backend/data/raw/scores/shandong_2024.json` | 20300 条，`source` 为 `sdzk.cn_2024`，`year` 为 2024；5721049 字节 |
| `data/raw/scores/shandong_2025.json` | 同样 21381 条、`sdzk.cn_2025`；5310712 字节，与 backend 那份同大小。没有做哈希比对 |
| `data/raw/scores/shandong_2024.json` | 同样 20300 条、`sdzk.cn_2024`；5030849 字节，和 backend 那份不一样大。没有逐条比对 |
| `backend/data/raw/scores/guangdong_2024_*.json`、`guangdong_2025_*.json` | 有 `year`（2024 或 2025），**没有** `source` 字段 |
| `backend/scripts/jiangsu_2025_physics.json` | `source` 形如 `jsjyksy_2025_*`，`year` 为 2025 |

`backend/data_pipeline/crawlers/province_easy.py` 能为河南、广东写出 `source: "mock"` 的假数据。本次在已提交的 JSON 里没有找到 `"source": "mock"`。`backend/data/raw/DATA_DOWNLOAD_CHECKLIST.md` 仍把广东 2024 标成待下载，和树上的 JSON 不一致，不能拿那份清单当库存。

本次没有重新下载考试院文件，也没有对照官网复核。文件里的年份和 `source` 字符串就是来源说明；它们不是录取建议。`confidence` 字段是档位常数（`confidence_kind: unvalidated_constant`），不是测过的概率。

## Docker Compose

文件在 `deploy/docker-compose.yml`：backend（SQLite 卷，8000）和 frontend（nginx，宿主 5173）。frontend 把 `/api/` 代理到 compose 服务名 `backend`。生产文件 `deploy/docker-compose.prod.yml` 要求环境变量 `SECRET_KEY`。开发 compose 不要求；未设置时进程内会生成临时密钥，重启后旧 token 失效。

本次审核环境没有 Docker，没有执行 `docker compose up`。不要把「文件存在」说成「已经启动成功」。

## GitHub About 替换文案

About 是仓库设置，这个 PR 改不到。当前 About 是：「AI 驱动的人生规划助手（FastAPI + React 18 + Claude API 可选）：学习/考试/高考志愿/职业等 21 个功能模块，Docker Compose 一键启动。」请换成：

> 个人全栈人生规划演示（FastAPI + React 18）。不是经过验证的建议，不是生产服务，也不是医疗、财务或招生指导。19 个后端模块；健康、财务、习惯页面仍是即将上线。Claude 可选。Compose 文件在 deploy/docker-compose.yml，本次审核没有启动容器。

Topics 里的 `saas`、`subscription` 不是已上线的付费产品。本仓没有支付集成。

## 作者机器上的路径

`F:/life-planner` 和 `F:\life-planner` 是原作者的 Windows 目录。clone、Compose 和 `make check` 都不会创建它。带这些路径的文件在开头有 `AUTHOR_PATH` 标记。`backend/app/middleware/trust_bd.py` 里指向仓库外 `test/2026-07-16-11-16-52` 的相对路径同样是作者机器上的布局。

## 失败方式

见 [FAILURE_MODES.md](./FAILURE_MODES.md)。

## 许可证

[MIT](./LICENSE)。
