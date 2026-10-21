# life-planner 立意收缩方案（SHRINK-PLAN v1.0，2026-09-07）

> 依据：用户「按立意收缩，聚焦 4 场景，打通 AI 和数据积累」指令 +
> `docs/REVIEW-VISION-2026-09-07.md` 立意审阅结论。
> 原则：收缩可回滚（软归档，不进 git 外的不可逆删除）；只动范围，不重写已封存逻辑；
> 数字全部可复算。

## 一、立意锚点（DESIGN.md 第 1 章）

- 一句话：陪伴用户「从高中到职场早期」的 AI 数据伙伴。
- MVP 4 场景：选科决策 → 考试错题分析 → 志愿填报 → 大学规划/求职准备。
- 护城河：数据从高中开始积累，「越用越准」。
- 明确不做：心理健康诊断、金融投资建议；愿景层（家庭/社交/亲密/旅行/心理/兴趣/意义/健康/习惯）非当前优先级。

## 二、模块裁剪清单（20 后端模块 + 3 前端聚合页）

### 保留（KEEP，4 场景 + 数据/AI 承重柱 + 基建）＝ 9 后端 + 2 前端聚合页

| 模块 | 对应立意 |
|---|---|
| dashboard | 仪表盘入口 |
| daily_tracker | 日常记录 = 数据积累载体（P0#4） |
| exam_analyzer | 考试错题分析（场景 2） |
| college | 志愿填报（场景 3） |
| career | 求职准备（场景 4） |
| recommend | 冲稳保智能推荐引擎（纯规则，已可离线用） |
| ai_coach | AI 教练（AI 灵魂） |
| life_planner | 人生目标（P0#5，数据） |
| auth | 登录/注册基建 |
| + subject-selection | 选科（场景 1，前端聚合页） |
| + study | 学习规划/大学规划（前端聚合页） |

### 归档（ARCHIVE，愿景层 + 明确不做）＝ 11 后端 + 1 前端

| 模块 | 归类 |
|---|---|
| finance | 明确不做（金融投资） |
| psychology | 明确不做（心理诊断·需资质） |
| family / social / intimacy / travel / meaning / interest / health / habits / learning | 愿景层（DESIGN 1.2「非当前优先级」） |
| + grad（前端） | P1/v2.0 考研，暂不做 |

> `learning` 后端模块与前端 `study` 学习规划页冗余，取 `study`（保留）、`learning`（归档）。
> 归档后：20 → 9 后端模块；菜单/路由 108 → 聚焦后约 60；页面 28 → 约 16。

## 三、AI 打通（支柱 1）

现状：`ai_client.py` 封装真实规范；`ANTHROPIC_API_KEY` 默认空 → 分析接口回
「AI 分析服务未配置」占位句；`AI_MODEL` 默认 `claude-sonnet-4-6`（需核对有效型号）。

方案（无 key 也交付核心价值，有 key 自动升级）：
1. **修默认模型号**：`AI_MODEL` 默认值改为 Anthropic 当前有效号（Claude Sonnet 现网最新 stable）。
2. **补齐规则降级**：`ai_coach` / `exam_analyzer` / `daily_tracker` 三处分析接口，在 AI 未启用时
   从「回占位句」升级为「本地确定性统计 + 模板反馈」：
   - 错题分析：不依赖 LLM，聚合错题科目/题型/知识点，给薄弱点排序 + 通用建议；
   - 日常反馈：按活动时长/类别统计给规则版反馈；
   - AI 教练：热门问题走模板回复 + 展示「接入 Claude 后升级为深度分析」。
3. **保留 LLM 升级路径**：`ANTHROPIC_API_KEY` 一设即自动切换，`coach_mode: llm|rule` 沿用。

## 四、数据积累打通（支柱 2：「越用越准」）

现状：`backend/data/` 有山东/广东 2024/2025 分数与位次（processed 已清洗），
`scripts/` 有 `seed_data.py` / `batch_import_all.py` / `import_shandong.py` / `import_guangdong.py`，
但 live 库 40 表 0 行——种子数据未入库，「越用越准」无运行证据。

方案：
1. **跑通种子入库**：用现有 import 脚本把已清洗的分数/位次装入库，校验行数可复算
   （替代 README 里 51k/2.5k 的无证据宣称，改为「已入库 N 行」的实际口径）。
2. **验证积累闭环**：确认 `daily_logs → build_user_summary → ai_client.chat(db,user_id)` 链路
   （fix C 已实现）确实随每日记录增多而把更多上下文注入 AI，产出「越用越准」脚本证据。

## 五、执行顺序与安全

1. 软归档 11 后端模块 → `backend/app/modules_archive/`；loader 发现式加载自然不再认领。
   前端归档 12 页 → 移出 `pages/` 到 `pages_archive/`，同步 `modules.ts` 菜单 + App.tsx 路由。
2. 跑 `check_module_menu.py` 漂移门 + `pytest` + tsc + 隔离 E2E（沿用「生产 users=0 / 测试库隔离」纪律）。
3. 数据入库 + AI 降级 + 模型号修正。
4. 更新 README/DESIGN 的模块/路由/页/数据行数口径（消除文档漂移）。

> 全部为软迁移，git 历史完整保留，任一步可 `git revert` 回滚。
> 生产 4800/8001 仅在验证通过后才由你决定是否重部署。