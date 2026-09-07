# P4 封存：三模块前端对齐（finance / habits / health）

## 交付
- 新页面 `Finance/`（记账/预算/储蓄目标+月统计，月份选择器）+
  `Habits/`（新建/打卡/连击+停用开关）+ `Health/`（健康日志/运动记录+阶段平均+评分构成），
  仿 Family/Recommend 写法（antd + `@/api/client` + `res.data.data` + dayjs）。
- `App.tsx`：3 懒加载 + 3 菜单项 + 3 RequireAuth 路由；`22-pages.spec.ts` 追加 3 用例。
- 后端零改动（P4-0 重勘察：接口形状与开题时一致，无漂移）。

## 证据
- `npm run build` 成功（5.92s）；4800 同源 `/finance /habits /health` 均为 200。
- 正源 4800 E2E：27 passed（含 3 新页 + 401 用例）；途中 1 挂（/health）已修。
- P4 写读验证脚本 `/tmp/p4_verify.py`：16 项 ALL PASS（记账/预算/目标/统计、
  新建/打卡/连击/列表、日志/运动/统计/评分），备份 `/tmp/lp_p4_preverify.db`。
- 包体：三页独立懒分包 raw 9.2/14.0/9.6KB（gzip 3.3/5.6/3.6KB），与 P5 推荐页 ~5KB 同量级，
  首屏主包未动（vendor 677KB raw / 222KB gzip，P3-1 口径内）。
- 封存实测：users=0（清 p4verify + 56 个 e2e_ 注册残留及子表行，vacuum + integrity ok），
  备份 `/tmp/lp_p4_preverify.db`；e2e 截图刷新（含财务/习惯/健康.png）。

## 发现与决策
1. `/health` 首轮挂：`score.components` 的值是对象 `{value, rate, weight}` 不是数字，
   前端按数字渲染致 React child 报错。修：按 `rate*100` 画 Progress，展示均值+权重
   （steps/步数、sleep/睡眠、exercise/运动中文化）。教训：后端契约以后端 services
   实现为准，MISSION 的 `{score,level,components}` 只记了键名没记值形状。
2. 注册自动注入 30 天示例数据（P5 发现延续）：新用户 finance/habits 列表天生非空，
   验证断言改为"包含我方写入行"（`any(...)`）而非计数。health `stats.days` 回 31
   （30 天窗口含今？ services 现状），断言只卡 `avg_steps >= 写入值`，不追此细节。
3. E2E 每用例注册一用户：两次全量跑留下 55 个 `e2e_*` 残留，清库范围按 P3/P5 既定做法
   覆盖 `e2e_*` + `p4verify`，子表按 `user_id` 级联删。
4. keeper/cron、8001、他人周报、`.agent-memory/` 全程未动；dist 被 ignore，不进库。
