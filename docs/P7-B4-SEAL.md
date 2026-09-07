# P7-B4 SEAL — 推送结构化：JSONL 事件 + 单用户失败隔离 + 日志落持久盘

## 动因
- 旧 `recommend_push.py` 只打印人话行 `slot=... users=...`，机器难解析；
  且一个用户异常即掀翻整批（`results = [push_for_user(...) for uid in ids]` 无 try）。
- cron 日志写 `/tmp/recommend_push.log`：本机重启后 /tmp 被清空，
  本次开工时该文件已不存在——P6 留的"明早查日志"证据链断过一次。

## 改了什么
- **`backend/scripts/recommend_push.py`**
  - 新增 `build_event(slot, results, errors, ts=None)` 纯函数：事件必含
    `ts/slot/users/recommendations/high/results/errors`；
    `users` 计 results+errors 两部分（失败用户也算数）。
  - 新增 `run_push(db, user_ids, slot)`：逐用户 try/except，异常
    `db.rollback()` 后记 `errors[{user_id, error}]`，同批其余用户照常推送。
  - `main()`：stdout 只打一行 JSON（`ensure_ascii=False`，中文可读，
    直接 `>>` 追加即 JSONL）；有 errors 时 exit 1（JSON 仍输出），
    全成功 exit 0。
  - docstring 内 cron 行同步为持久路径（之前是 /tmp）。
- **crontab**：推送 3 行（08:00 morning / 21:00 evening / @reboot 兜底）
  重定向由 `/tmp/recommend_push.log` 改为
  `backend/logs/recommend_push.jsonl`（`*.log`/`logs/` 在 .gitignore，不进仓库）。
  keeper 2 行逐字保留（迁移脚本断言 5 行中只动第 3–5 行且都含 recommend_push.py）。
- **新增 `backend/tests/test_recommend_push.py`**（3 用例）：
  事件键/汇总数/单行 JSON 回环；monkeypatch 让 uid 999 抛 RuntimeError，
  同批 1000 照常推送且 errors 点名；errors 计入 users。

## 验收证据
- pytest：**82 passed, 18 skipped**（P6 基线 79 + 本刀 3，无回归）。
- scratch 库实跑（`DATABASE_URL=/tmp/lp_b4_push_smoke.db`，事后已删）：
  stdout 单行 JSON，keys=`errors/high/recommendations/results/slot/ts/users`，
  exit=0；`--user-id 424242`（不存在用户）得 onboarding 推荐 1 条，
  exit=0（sqlite 默认无 FK 强校验——如实记录）。
- exit=1 路径由单测覆盖（monkeypatch 抛错 → errors 非空），未在 live 库演练。
- 生产只读核验：4800/8001 均为 200；正式库 `users=0`；
  keeper/cron 除推送 3 行外未动；他人周报未跟踪文件未动。

## 遗留（B5）
- 新日志文件首次自然写入待今晚 21:00（旧 /tmp 日志已随重启消失，无法补）。
- B5 QUICKSTART/make 收口（含 `make check` 收编一致性脚本、`make migrate`）。
