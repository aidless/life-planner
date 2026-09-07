# P7-B5 SEAL — QUICKSTART/make 收口：P7 全剧终

## 改了什么
- **新增根目录 `Makefile`**（6 目标）：`help/test/check/check-menu/check-drift/migrate/health`。
  校验脚本统一以 `backend/` 为 cwd 跑；`migrate` 无 `DATABASE_URL` 直接 exit 2 拒绝
  （防误写生产库——repo 里默认 URL 指向 `./life_planner.db` 相对路径，裸跑必出事）。
- **`QUICKSTART.md`**：新增 "Makefile 收口" 一节（P7 现状：discovery 加载、create_all 仍开机、
  migrate 维护窗口专用、新表必配 migration、动态菜单）；顺手修两处过期——
  cron 推送 2 条→3 条（B4 加了 @reboot 兜底），推送日志 /tmp→`backend/logs/recommend_push.jsonl`。

## 验收证据
- `make check-menu`：CHECK-OK（19 声明域一致；4 未认领路由 INFO 允许）。
- `make check-drift`：A tables=40 B tables=40 → PARITY-OK。
- `make migrate` 无 DATABASE_URL：拒绝 exit 2；`DATABASE_URL=sqlite:////tmp/lp_b5_mig.db` 实跑：
  001→002→003 全绿，41 表（含 alembic_version），scratch 事后已删。
- `make test`：82 passed, 18 skipped（与 B4 一致，无回归）。
- 生产只读核验：4800 `/api/health` healthy；正式库 `users=0`；crontab 推送 3 行；
  keeper/cron/服务未重启未改动；他人周报未跟踪文件未动。

## 遗留（P7 关账，B0–B5 全封）
- 生产 stamp head + `upgrade head` 接管启动：待维护窗口（`make migrate` 已就绪）。
- live 菜单真实渲染目检：待后端重启后（B3 fallback parity 已保底）。
- 今晚 21:00 新 JSONL 日志首次自然写入（B4）。
- push 远端：token 失效中，提交暂只在本地（各刀同）。
