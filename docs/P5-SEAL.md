# P5 封存：实时决策推荐系统（混合引擎）

## 交付
- 后端新模块 `recommend/`：rules（纯函数 9 规则 H1/H2/H3/F1/F2/F3/HE1/HE2/D1/EMPTY，
  阈值单源 THRESHOLDS）+ services（快照/落盘/通知幂等）+ router
 （GET today/history/notifications，POST notifications/{id}/read）+ models
 （recommendation_runs/notifications）。
- LLM 润色层：有密钥则 1 次 analyze 只写文案（prompt 禁止编数字），
  无密钥/异常 → coach_mode=rule 降级，永不 500。
- 定时推送 `scripts/recommend_push.py` + cron 08:00/21:00（morning/evening），
  幂等（同用户同日同规则不重复推）。
- 前端 `/recommend`（今日推荐+教练一句话+通知箱+7天快照）+ 菜单入口 +
  header 铃铛（未读数）；推荐页独立懒分包约 5KB。
- 迁移 `migrations/versions/002_recommend.py`（dev 库由 create_all 自建）。

## 证据
- pytest：test_recommend_rules 14 + test_recommend_api 5 = 19 全绿。
- 正源 4800 E2E：23 passed + 1 flake（/daily 截图协议抖动，单跑通过，非产品回归）；
  含新增 /recommend 用例。
- 包体：推荐页独立分包 ~5KB raw，无首屏回归（P3-1 194KB 口径不变）。
- 封存实测：4800=200，cron 4 条在位（keeper×2 + 推送×2），users=0（删 36 测试号 +
  34 子表 7384 行，integrity ok），备份 /tmp/lp_p5_pree2eclean.db。

## 发现与决策
1. 注册自动注入 30 天示例数据（W35 auth.router）——新用户永不为空，
   EMPTY 规则只走纯函数单测；API 测试断言改为种子用户结构检查。
2. cron 安装时沿用追加方式，keeper 双条未动；8001 他人物件全程未动。
3. P4 三模块前端页暂停，MISSION 存档于 .agent-memory/p4-frontend-align/（未跟踪）。
4. 密钥仍缺席：coach_mode=rule 为当前生产行为；用户提供 ANTHROPIC_API_KEY 后
   LLM 润色自动生效，无需改代码（费用确认路由回用户）。
