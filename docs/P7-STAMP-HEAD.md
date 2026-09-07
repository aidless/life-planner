# 生产 stamp head 操作记录（2026-09-07，P7-B1 遗留项关闭）

## 做了什么（按顺序）
1. 备份：`backend/backups/life_planner.db.pre-stamp-20260907`（704512 字节，未进 git）。
2. 预检：`alembic_version` 空表（B1 起预先存在，非迁移写入）、`users/exams/exam_questions` 三表全 0 行、4800 healthy。
3. `alembic stamp head`（显式 DATABASE_URL 指向正式库）：`current` → `003_baseline_parity (head)`。
4. 验后 parity（只读反射 vs 双 metadata）报 users/exams/exam_questions 列差异——stamp 只写版本号、
   不跑 003，生产三表仍是旧列集合（空表，无数据风险）。
5. 纠正：`stamp 002_recommend` → `upgrade head`，003 把三张空表重建为 AppBase 新形；
   `current` 回到 head，4800 全程 healthy。

## 判定口径纠正（本轮教训）
- 第一版 parity 脚本用了双 metadata 列**并集**，把 LegacyBase 独有列（phone/exam_name/content…）
  也算进期望，误报 DIVERGED。
- 003 的真实口径是 AppBase 优先（`update` + `setdefault`，L97-100）：重叠表以新形为准。
  按同口径复刻脚本复核：`003-PARITY-OK`（40 表，表+列双齐）。
- `alembic check` 在此库上不可用：双 metadata 有重叠表名，autogenerate 路径直接抛
  `Duplicate table keys`（B1 已知局限，非漂移）。以后验 parity 用 003 同口径脚本，不用 `alembic check`。

## 终态
- `current` = `003_baseline_parity (head)`；003 口径 parity OK；`users=0`；4800 healthy、8001 200。
- 运行中后端仍是 stamp 前的老代码（`GET /api/modules` 404），未重启——重启切 live 菜单待用户择机。
- 代码树零改动（只有正式库文件变化 + 备份 + 本记录）；远端未推（token 失效，老问题）。
