# P7-B3 SEAL — 前端切片：菜单数据源切到后端自声明，路由保持静态

## 动因
- B0/B2 遗留：前端菜单 22 项硬编码于 `App.tsx`，后端 manifests 改了前端无感知，
  `check_module_menu.py` 只是事后漂移网。删域演练时菜单不会自动下线被删域。

## 改了什么
- **新增 `frontend/src/config/modules.ts`**：19 个声明域 `{name,title,path,menu}` 静态镜像
  （首屏/降级菜单），+ `EXTRA_MENU`（3 无后端域聚合页：/study、/subject-selection、/grad，
  位置锚定到镜像 path，live/fallback 两模式都追加）。
- **新增 `frontend/src/hooks/useModules.ts`**：首屏直接渲染 fallback（零闪烁）；
  挂载后 `GET /api/modules`，成功取交集按镜像排序、未知 path 丢弃、聚合页交错追加；
  任何失败静默保持 fallback。静态 `<Route>` 全保留——被删域深链仍可达（页面内 API
  自会失败），只是不再出现在导航里。
- **`App.tsx`**：删 22 行硬编码 `menuItems`，改 `useModules()`；桌面端补 `<Link>`
  （旧代码 header 包 span 丢导航已顺手修；移动端原来 Link 套 Link，顺手解嵌）。
- **`check_module_menu.py`**：App.tsx 侧改断言消费 `useModules()`；菜单键/文案断言改走
  镜像+EXTRA_MENU；新增 `_check_mirror` 三元组双向比对（缺失/残留即 exit 1）。

## 计划修正（有证据）
1. **EXTRA_MENU 锚点修过一次**：初版 `/subject-selection` 锚到 `/study`（非镜像 path，
   被丢弃，parity 脚本 21≠22 揪出），改锚 `/goals` 后 22/22。
2. **块注释 `*/` 坑**：modules.ts 头注释里写了 `modules/*/manifest.py` 提前闭合注释，
   tsc/esbuild 双炸；改写措辞，后人注释里禁写 `*/`。
3. **生产 4800 仍是旧后端**（/api/modules 404，进程 10:31 早于 B0 提交 11:52）：
   不重启是故意的——新 dist 已原地生效，走 fallback 菜单，UX 与旧版逐项一致（parity 实证）；
   待后端重启后自动切 live，无需再发版。

## 验收证据
- `check_module_menu.py`：CHECK-OK（19 声明域路由+菜单一致；5 未认领路由 INFO 允许）。
- `tsc --noEmit` 0；`vite build` 6.99s 成功（dist 原地更新，4800 即时生效）。
- fallback parity 脚本：新旧菜单顺序 22/22 全等（证据 /tmp/old_menu.txt 方法可重跑）。
- 临时端口 smoke（4809+scratch DB，新代码）：/api/modules 200（count=20，其中 19 有
  frontend_path）+ / 200 + X-Request-ID 头 verified；进程已杀，scratch DB 已删。
- pytest：79 passed, 18 skipped（与 P6 基线一致）。
- 生产只读核验：4800/8001 全程 healthy；正式库 `users=0`；keeper/cron 未动；
  他人周报未跟踪文件未动。

## 遗留（B4/B5）
- live 菜单真实渲染待后端重启后目检（或下次 E2E 截图）。
- B4 推送结构化、B5 QUICKSTART/make 收口（含 `make check` 把本脚本收编）。
