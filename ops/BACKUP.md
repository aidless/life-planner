# 备份流程（P6 落盘）

封存/清库类操作前必须先快照正式库，后果自负项。

## 位置

- 正式位置：`data/backups/`（`*.db` 在 `.gitignore`，不进仓库，重启不丢）
- 禁止只放 `/tmp`（重启即丢；P6 前 6 个封存备份全在 `/tmp`，已迁回此处）

## 命名

`lp_<阶段>_pre<动作>_<YYYYMMDD_HHMMSS>.db`，例：
`lp_p6_pree2eclean_20260907_113900.db`

## 时机

1. E2E 前（E2E 注册产生测试号）
2. pytest 全量前（活体 B4 测试写正式库，需 `LP_LIVE_TESTS=1` 才跑）
3. 任何 `delete from users` 前

## 恢复

```bash
cp data/backups/lp_<name>.db backend/life_planner.db
# cwd=backend 时正式库是 backend/life_planner.db（4800/8001 服务用它）；
# 仓库根 life_planner.db 是 pytest 旧 cwd 残留，不用、P6 已删。
```

## 现存备份（2026-09-07 落盘，均 integrity ok）

| 文件 | users | 说明 |
|---|---|---|
| lp-backup-p22.db | 58 | P22 备份 |
| lp_p33_predelete_20260907_100437.db | 81 | P3-3 删除前 |
| lp_p32_pree2eclean.db | 49 | P3-2 E2E 前 |
| lp_p5_pree2eclean.db | 36 | P5 E2E 前 |
| lp_p4_preverify.db | 55 | P4 验证前 |
| lp_review_predbclean.db | 62 | 重审清库前 |
