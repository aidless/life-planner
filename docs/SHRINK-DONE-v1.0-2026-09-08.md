# SHRINK-PLAN v1.0 执行报告（2026-09-08）

> 依据：`docs/SHRINK-PLAN-v1.0.md` + 用户指令「life-planner按SHRINK-PLAN执行：
> 软归档11模块+数据入库+AI规则降级+修模型号」。
> 原则：软迁移可回滚；数字全部可复算；生产 4800/8001 全程未重启、users 恒为 0。

## 一、软归档（后端 11 域 + 前端 12 页）

### 后端（`backend/app/modules/` → `backend/app/modules_archive/`）
归档 11 域：finance / psychology / family / social / intimacy / travel /
meaning / interest / health / habits / learning。

- 移动后重写各域内部 `app.modules.<self>` → `app.modules_archive.<self>`（每域 2 文件）。
- `loader.py` 新增 `load_archive_models()`：归档域 **models 仍登记**进
  `AppBase.metadata`（表结构/历史数据保留，回滚零成本）。
- `main.py` / `migrations/env.py` / `check_db_drift.py` 三处均在 create_all /
  迁移路径前调用 `load_archive_models()`，保持 alembic↔create_all parity。
- `discover()` 现返回 **9 个活跃域**（8 个声明前端 + auth）。

### 前端（`frontend/src/pages/` → `pages_archive/`）
归档 12 页：Family / Finance / GradAdvisor / Habits / Health / Interest /
Intimacy / Learning / Meaning / Psychology / Social / Travel。

- `config/modules.ts`：FALLBACK 菜单 19 → 8 项；EXTRA_MENU 去掉 `/grad`。
- `App.tsx`：删 12 个懒加载 + 12 个路由（/grad /finance /habits /health
  /psychology /family /interest /social /learning /travel /intimacy /meaning）。
- 孤儿组件 `components/AppLayout.tsx` 同步去掉 GradAdvisor 引用。
- E2E `25-pages.spec.ts` → `13-pages.spec.ts`（PAGES 25 → 13）。

### 注册侧
`scripts/init_user_data.py`：归档域改为可选导入 + `_ARCHIVED_DOMAINS` 显式跳过——
新用户注册不再注入愿景层示例数据（`auth/register` 原 try/except 兜底不变）。

## 二、数据入库（支柱 2：verifiable「越用越准」载体）

`backend/scripts/import_json_scores.py`（新，幂等可复算）读 `data/raw` 已清洗 JSON：

| 表 | 行数 | 说明 |
|---|---|---|
| `college_scores` | **50,865** | 山东 2024(20,265)+2025(21,269)+广东 2024(4,393)+2025(4,938)，原始 51,012 去重 147 |
| `province_ranks` | **550** | 山东 2025 一分一段 |

覆盖省/年 = 山东 2024/2025 + 广东 2024/2025。`college_info` 仍 0 行（暂无数据源）。
`users` 恒 **0**（未写用户数据）。已备份
`life_planner.db.bak-import-20260908-230102`。

## 三、AI 规则降级（支柱 1：无 key 也交付核心价值）

`app/shared/ai_client.py` 三处分析接口在 `ANTHROPIC_API_KEY` 未设时，从「回占位句」
升级为**本地确定性统计 + 模板反馈**（数字由真实入参计算，非 LLM 编造）：
- `analyze_daily_log` → 活动条数/总时长/按类汇计/平均心情精力/投入最多项。
- `analyze_exam` → 错题数/得分率/按知识点聚错排序（前 5）+ 订正建议。
- `chat`（/api/ai/chat）→ 分模块热门问题模板 + 提示「设 key 后升级 Claude」。
`ANTHROPIC_API_KEY` 一设即自动切 Claude，无需改码。

## 四、模型号核对

`AI_MODEL` 默认 `claude-sonnet-4-6` 经 liteLLM Anthropic provider 清单核实为
**有效 dateless 型号**（dateless 别名恒定指向该代最新快照），无需改动；已在
`config.py` 加注释固定结论与出处。

## 五、门禁结果（全部 PASS）

| 门禁 | 结果 |
|---|---|
| `check_module_menu.py` | CHECK-OK：8 个声明域路由+菜单一致 |
| `check_db_drift.py` | PARITY-OK：A=40 B=40 |
| `pytest` | 82 passed + 18 skipped（活体） |
| `tsc --noEmit` | 0 错 |
| `vite build` | ✓ built |

## 六、生产状态

- 4800（后端）healthy；8001（前端）healthy；**未重启**。
- live 库 `users=0`、`college_scores=50,865`、`province_ranks=550`。
- 改动均在工作区（未 commit），与上一批视觉改动一致。

## 七、遗留与建议（如实）

1. **Dashboard 12 维聚合**：`build_dashboard` 仍聚合 12 维，11 个归档维经
   `_opt` 可选依赖降级为 score=0，前端仍显示这些「待提升 0」维度及死链。本次按
   「只动范围」未重写；建议下一批决定：裁掉归档维只留学业/职业，或接受现状。
2. **`college_info` 无数据源**：README 原「2.5k 大学」罝换成「0 行，暂无数据源」，
   未杜撰。
3. **mypy 未装**：本机未安装 mypy，本次未跑；静态正确性由 pytest + tsc 兜底。
4. **回滚**：任一步 `git checkout`/反向移动即可；归档目录与 git 历史全保留。