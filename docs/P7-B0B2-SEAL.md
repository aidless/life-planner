# P7-B0/B2 SEAL — 模块化单体首刀：发现式加载 + 网关薄层

## 改了什么
- **B0 发现式加载**：20 个域各加 `manifest.py`（name/title/router/frontend/cron 自声明）；
  `main.py` 删除 50+ 行手工 import + include_router，改 `loader.discover()` 自动注册；
  models 副作用导入先于 `create_all`（P1-fix 的 Base 先建/Legacy 后建语义保留）。
- **新增 `GET /api/modules`**：域聚合（name/title/api_prefix/frontend_path/menu/cron），供菜单校验与管理面。
- **新增 `scripts/check_module_menu.py`**：manifests ↔ `App.tsx` 路由/菜单一致性校验，漂移即 exit 1。
- **聚合域可选依赖化**：`dashboard/services.py` 12 域硬 import → `_opt` 桩（调用点本就有 try/except，
  自动降级）；`recommend/services.py` finance/habits/health/daily 模块级 import → `_optmod` 桩 +
  `collect_snapshot` 分段 try/except + budgets 守卫 + HabitCheckin 懒导入。
- **B2 网关薄层**：新增 `RequestIdMiddleware`（X-Request-ID，加法，业务零改动）；
  新增 `app/shared/envelope.py` ok()/fail()（新代码用，不重写旧 router）；
  限流换 Redis 阈值明确化（429 率连续 1 天 >1% 才换）；修正前端 `ApiResponse` 类型。

## 计划修正（有证据）
1. **包络不迁移**：原计划 `{ok,...}`，实测前端契约是 `{success,data,error}`（client.ts/services/api.ts/
   Dashboard 在用，限流中间件 W29.2 也是此格式）。改迁移为锁定，修 stale 类型。25 页零改动。
2. **pkgutil → 直接读目录**：ntfs 上 `pkgutil.iter_modules` 漏扫 college（21 里缺它，复现确认），
   loader 改 `os.listdir` 找 manifest.py，确定性 20/20。
3. **删域判据细化**：删目录只下线路由；若聚合域（dashboard/recommend）跨域引用了它，
   本次已顺手可选依赖化，演练通过。今后删域前仍建议 grep 谁 import 了它。

## 验收证据
- pytest：79 passed, 18 skipped（与 P6 基线一致），正式库 users 全程 0。
- check_module_menu：20 域，19 个声明映射一致；6 条未认领前端路由为跨域聚合页（INFO 允许）。
- 删域演练（meaning 移出）：启动成功 19 域，/api/meaning 404，dashboard/recommend 各 200 降级；恢复后 20 域 CHECK-OK。
- tsc --noEmit 0；vite build 6.39s 成功（类型变更无运行时差量，dist 原地更新，4800 即时生效）。
- 临时端口 smoke（4801+scratch DB）：/、/api/health、/api/modules、/recommend、/finance、/health 全 200，
  /api/nonexistent 404；X-Request-ID 头 verified。临时进程已杀，scratch DB 已删。
- 生产 4800/keeper/cron 全程未动；他人周报未跟踪文件未动。

## 遗留（B1/B3-B5）
- Alembic 基线化未做（仍 create_all）；users 表归属 auth 已是事实，无需动。
- 前端菜单仍硬编码，check 脚本是漂移网；动态菜单待 B3。
- QUICKSTART/make 收口待 B5。
