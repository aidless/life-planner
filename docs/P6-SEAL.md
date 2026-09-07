# P6 封存：重审 4 建议 + 2 附带（2026-09-07）

## 交付
1. **测试隔离**：`backend/tests/conftest.py` 在任何 app 导入前把
   `DATABASE_URL` 指到绝对路径独立库
   `backend/tests/test_isolated.db`（异步兼容式 `sqlite+aiosqlite`，
   `*.db` 已 gitignore）。`backend/app/database.py` 同步 engine 侧
   strip `+aiosqlite`（默认 URL 无后缀时为 no-op，生产行为不变）。
   B4 活体测试（`test_b4_*.py` 走真实 HTTP 打 8001，不受隔离约束）
   加 `LP_LIVE_TESTS` opt-in 门：默认 skip，显式置 1 才跑。
2. **QUICKSTART**：顶部新增"生产态访问"一节（4800 单源 + 健康检查 +
   /recommend + cron + keeper + 5173/8080/8001 退役声明）。
   docker 小节的 5173 属实（dev 容器端口），保留。
3. **推送**：根因=机器今晨 09:11 重启，08:00 时刻宕机故未触发（脚本无辜，
   手工同命令跑通 `slot=morning users=0`）。加 `@reboot sleep 120`
   morning 补跑（save_run 幂等，去重安全）；cron 现 5 条。
   首次自然触发证据待今晚 21:00（`/tmp/recommend_push.log` 查）。
4. **备份**：6 个 `/tmp` 封存备份迁入 `data/backups/`（integrity 全 ok），
   新建 `ops/BACKUP.md`（位置/命名/时机/恢复四约定）。
5. 附带：仓库根残留 `life_planner.db`（95 smoke 号旧 cwd 污染）快照后删除；
   `22-pages.spec.ts` 改名 `25-pages.spec.ts`（25 页 + 404 + 401 = 27 用例）。

## 证据
- pytest：79 passed + 18 skipped（B4 活体默认跳）7.4s；正式库 users 全程 0。
- 正源 4800 E2E：27 passed 20.2s（改名后首跑）；清 27 e2e_ 号 + 5535 行，
  users=0，integrity ok。
- QUICKSTART 照做：`/api/health`=200，`/recommend`=200，`/finance`=200。
- 备份找回演练：`lp_p6_pree2e` 拷 /tmp 恢复 drill，integrity ok。
- cron：`crontab -l` 5 条（keeper×2 + 推送×2 + reboot 兜底×1）。
- 归零链：B4 误污染 28 号 + 5740 行（本次 pytest 触发）→ dry-run 核对 →
  全删 + vacuum；E2E 27 号 + 5535 行 → 同流程。两次断言"无非测试行"才执行。

## 发现与决策
1. 双 settings 并存（`app/config` 同步式 vs legacy `config` 异步式）是本次
   隔离最大坑：第一版同步式 URL 直接炸 legacy async engine（65 errors），
   改异步统一式 + 同步侧 strip 后解决。后人改 URL 形式必跑全量 pytest。
2. 8001 为他人运维资产：B4 门只做"默认不碰"，opt-in 运行仍打 8001，
   跑完须自清（本轮即实例）。keeper/8001 进程全程未动。
3. `docs/REVIEW-2026-09-07.md` 仍未跟踪（重审报告提交待用户确认），
   本封存不代收。`.agent-memory/`、4 周报（他人）同前未动。
4. 今晚 21:00 为推送首次自然触发：明早查 `/tmp/recommend_push.log`
   有 morning/evening 行即闭环；无则开 P6-1。
