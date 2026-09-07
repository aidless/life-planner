# P7-B1 SEAL — Alembic 基线化：alembic-head 与 create_all 收敛

## 动因（诚实账）
- B0/B2 遗留：启动仍靠 `create_all`，migrations/ 只是摆设——而且是**坏的摆设**：
  1. `migrations/env.py` 顶层 `from database import Base` 触发 `create_async_engine`，
     传同步 URL 直接炸（`The asyncio extension requires an async driver`），alembic 全不可用；
  2. `001` 是 legacy 快照：users/exams/exam_questions 是旧表结构（phone/exam_name/content 时代），
     且缺 ~29 张新域表；生产实际是 `Base.metadata.create_all` 且 Base 优先。
     即 alembic-head 与生产 schema 是**两个东西**。

## 改了什么
- **`migrations/env.py` 重写**：DATABASE_URL 先归一化（import 前保证 async 式，
  迁移连接用 sync 式），再注册模型（`loader.discover()` + legacy `models`），
  `target_metadata=[AppBase, LegacyBase]`，副作用 engine 零执行。
- **新增 `migrations/versions/003_baseline_parity.py`**（revises 002）：
  1. 双 metadata `create_all(checkfirst)` 补齐缺表（`already exists` 索引残留视为收敛信号容忍，其余重抛）；
  2. 全量列名比对：凡 DB 已有但与当前 metadata 列集合不一致的表——空表重建到当前结构
     （旧表改名备份→建新→交集列回灌→删备份，备份表索引先清以避 sqlite 全局索引名冲突）；
     非空旧表**直接 abort**（`RuntimeError: refuses ... Port the rows by hand`），拒绝静默丢数；
     仅顺序不同视为无差异（sqlite 定义序即 DDL 差异，此处放行并记录为 B1 已知局限，类型/默认值差异同）。
  3. `downgrade()` 故意单向（抛错）：基线回滚请从文件备份恢复。
- **新增 `scripts/check_db_drift.py`**（漂移门禁）：scratch A（双 create_all）vs scratch B
  （空库 `upgrade head`），比表集合+逐表列名+三张历史重塑表的新形断言；漂移即 exit 1。
- 生产 4800 **未动**：仍 `create_all` 启动；已存在库的 `alembic stamp head` 推迟到维护窗口（B1 不做）。

## 验收证据
- `check_db_drift.py`：第一跑即揪出 `college_scores` 漂移（001 的 rank_min vs 当前 min_rank/min_score/subject_type），
  003 泛化后 `A tables=40 B tables=40 -> PARITY-OK`（表+列双 parity）。
- `alembic upgrade head` 空库直跑：001→002→003 全绿，`current` 停 `003_baseline_parity (head)`。
- 非空旧表门禁实测：002 处 users 塞 1 行 legacy 数据再升 head，003 按预期拒绝并点名差异列。
- pytest：79 passed, 18 skipped（与 P6 基线一致）。
- 生产只读核验：`curl 4800/api/health` healthy；正式库 `users=0`；服务/cron/keeper 未重启未改动。
- 观察记录（未证实归因，不算结论）：正式库文件 mtime 在 B1 窗口内动过（约 11:55），最可能是测试启动
  create_all 触碰；行数证据 users=0、服务全程 healthy，无数据写入迹象。正式库内有**预先存在**的空
  `alembic_version` 表（0 行，非 B1 写入——B1 所有迁移只跑在 /tmp scratch 库）。

## 遗留（B3-B5）
- `main.py` 启动仍 `create_all`（行为零变化是故意的）；`upgrade head` 接管启动待维护窗口 stamp 之后。
- 新表以后必须配 migration（门禁脚本会盯）；B5 把 `make migrate`/`check` 收进 QUICKSTART。
