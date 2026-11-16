# PREREG — life-planner 预注册与评测规格

> 本文件是 life-planner 的**预注册规格**（registered-report 风格）：声明本仓库**实际存在、可从落盘证据复算**的 API/模块/测试结构假设、评测方案、成功标准与明确边界。
> 所有数字来自仓库内文件（`backend/app/`、`backend/tests/`、`bench/results.json`）与 AST 静态分析，**不是虚构实验**。

---

## 0. 一句话假设（先读这行）

> life-planner 是一个 FastAPI + React 全栈演示。模块数、OpenAPI 操作数和默认 pytest 的 passed/skipped 以 README 的 honesty 块为准，由 `backend/tests/test_honesty_drift.py` 重算。无 Claude key 时 AI 教练返回固定的「未配置」字符串。

---

## 1. 主假设 H1（业务模块注册结构）

- **假设**：`backend/app/modules/*/router.py` 的个数等于 README honesty 块的 `backend_modules`。
- **可证伪方向**：漂移测试失败。
- **评测方案**：`backend/tests/test_honesty_drift.py`。
- **成功标准**：该测试通过。不要另写一个手抄的模块数。

## 2. 假设 H2（测试套件结构）

- **假设**：默认 pytest（无 `ANTHROPIC_API_KEY`、无 `B4_INTEGRATION`）的 passed 与 skipped 等于 README honesty 块。
- **可证伪方向**：漂移测试失败。
- **评测方案**：`backend/tests/test_honesty_drift.py` 起一个子进程跑 pytest 并解析汇总行。
- **成功标准**：该测试通过。跳过的部分是 B4，不是核心功能已经测过。

## 3. 假设 H3（AI 教练 fail-closed）

- **假设**：无 `ANTHROPIC_API_KEY` 时，AI 教练返回**显式**"AI 分析服务未配置（缺少 ANTHROPIC_API_KEY）"，不假装成功。
- **可证伪方向**：若无 key 时 AI 教练返回成功或空串，则 H3 不成立。
- **评测方案**：`backend/app/shared/ai_client.py:34-35`（`if not self.enabled: return "AI 分析服务未配置..."`）；`config.py:41` `ANTHROPIC_API_KEY = os.getenv(..., "")` 默认空。
- **成功标准**：无 key → `enabled=False` → 显式"未配置"字符串。

## 4. 假设 H4（核心功能不依赖 key）

- **假设**：计划、记录、目标、仪表盘等核心 CRUD 在无 key 时照常工作。
- **可证伪方向**：若核心端点无 key 时返回 5xx，则 H4 不成立。
- **评测方案**：核心模块路由不注入 `ai_client` 依赖；`ai_client.enabled=False` 时 `analyze` 走未配置分支。
- **成功标准**：核心 CRUD 不触碰 `ai_client`；无 key 照常工作。

---

## 5. 明确边界（不证明什么）

| 维度 | 不证明 | 原因 |
|---|---|---|
| B4 集成测试完整性 | 18 项 B4 集成**未跑** | 需仓库外私有 `trust-cap` 包 + 8001 live backend + `B4_INTEGRATION=1` |
| TrustBoundaryMiddleware 完整保护 | 无 `trust_cap` 包时**静默禁用**（降级） | `main.py:183` 捕获 ImportError 后仅 warning，**不是完整保护** |
| 健康/财务/习惯前端 | 这些维度已完整可用 | 前端仍在建设，仪表盘标「即将上线」，不显示分数 |
| API 稳定性 | honesty 块里的 operation 数是稳定对外承诺 | 它是当前 `app.openapi()` 的计数，变了就要改 README，否则漂移测试失败 |
| 性能（HTTP 延迟） | 端到端请求延迟 | 本基准只测 AST 结构解析，不含真实 HTTP 往返（需完整依赖） |

---

## 6. 结论纪律

- 所有数字从本仓重算（见 README「复算」节 + `bench/structure_bench.py`）。
- B4 的 18 项集成测试**不构成**对 B4 完整性的经验证据（本机未跑）。
- TrustBoundaryMiddleware 在无 `trust_cap` 时为**降级**状态——安全边界声明必须如实说明，不得声称完整保护。
- 本 PREREG 是规格声明，不新增实验，不改变已冻结路由/模块/测试结构。
