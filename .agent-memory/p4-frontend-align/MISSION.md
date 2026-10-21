# P4 MISSION：三模块前端对齐（finance / habits / health）

- 目标：三个已有完整后端（models/router/schemas/services 五件套）的模块补齐前端页面，
  路由入口 + 列表/新增/编辑（打卡）/删除（停用），联调同源 4800，E2E 全绿后提交封存。
- 验收标准：
  1. `/finance` `/habits` `/health` 三路由 RequireAuth 可达，菜单有入口；
  2. 每个页面至少覆盖其后端核心写 + 读接口（finance：记账/预算/目标+统计；
     habits：新建/打卡/连击；health：日志/运动/评分）；
  3. 正源（4800 同源）E2E 全绿；users 归零；提交 + tag。
- 阶段：P4-1 finance 页 → P4-2 habits 页 → P4-3 health 页 → P4-4 联调/E2E/封存。
- 约定：仿 Family/index.tsx 写法，直调 `@/api/client`（baseURL 已含 /api）；
  ApiResponse 信封取 `res.data.data`；日期用 dayjs 格式化；bash 路径一律 /data3。
- 后端接口形状（已勘察，证据在本会话）：
  - finance：POST/GET transactions/budgets/goals，GET stats?month=YYYY-MM；
  - habits：POST/GET `/api/habits`（注意无尾斜杠），PUT /{id}，POST /{id}/checkin{date,completed,note}，
    GET /{id}/streak{current_streak,longest_streak,total_checkins}；
  - health：POST/GET logs?days&exercises?days，GET stats?days，GET score{score,level,components}。
