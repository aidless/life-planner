# P3 封存（2026-09-07）：生产加固三站闭环

## 三站交付
- P3-1 包体取证（c67a89d）：sourcemap 拆包证实 602KB 入口含 168 个 antd 源文件、全路由共享，树摇后已是下限；
  gzip 实测 194KB，500KB 警告线系 min 体积口径属误报。删 4 个零引用依赖（recharts、react-query v3、
  tanstack v5；lodash 实为传递依赖不在清单内），生产 sourcemap 关闭（曾占 6.3MB）。
- P3-3 清库（9ec6ee9）：删前复点 81 个非 58 个——多出 23 个 e2e_ 系 P3-1 当日 E2E 自产；全表审计 100% 机器号
  后连带清除。删 users 81 + 24 张子表 16605 行，vacuum 后 integrity ok。备份 /tmp/lp_p33_predelete_20260907_100437.db。
- P3-2 常驻化（0580884）：无 sudo，cron 双条目兜底（@reboot + 每 5 分钟 keeper）。
  复测首跑 22/23 系错配独立 serve 基址（5173 无 /api 代理，index.html 被当 200 吞进 Table 必崩），
  非产品回归；独立 serve 当场退役，keeper 只保活后端 4800。正源 23 passed 15.9s。
  删本次 49 测试号，users 归零。备份 /tmp/lp_p32_pree2eclean.db。

## 封存时刻实测（2026-09-07 ~10:2x）
- 后端 4800 = 200，前端同源 = 200，cron 两条 life-planner 在位，users = 0，git 树干净（仅 4 个他人周报未跟踪）。
- 4800 服务进程为 10:11 启动——非 P3-2 当时拉起者，系 keeper 或外部重启，服务自愈成立。

## 环境异常声明（本轮封存中发现）
1. docs/LIFEMEMO.md（未跟踪的工作笔记）因环境视图切换丢失，git 无记录；本封存由 git log + 会话证据重建。
2. 路径双视图：文件工具走 F:/ 视图、bash 走 /data3 视图，同一仓库（commit 链一致已证）；
   bash 一律用 /data3/projects/life-planner，venv 是 backend/venv（P2 记录 .venv 笔误）。
3. @reboot 条未实测（不能重启开发机），5 分钟 keeper 保活已实证。
4. 8001 他人后端（09:53 启动）全程未动；本机无 sqlite3 CLI，库查询走 venv python。
5. 教训账本 ledger/lessons.md 在当前视图无落点，教训暂存本节：
   L-P3-1 未跟踪文件不是证据，关键笔记要么进 git 要么进账本；
   L-P3-2 E2E 基址错配时先查网络返回体再怀疑产品；
   L-P3-3 删库前先复点数量，差异即停手审计。

## 标签
p3-sealed（0580884 起算链上追加本封存提交）。
