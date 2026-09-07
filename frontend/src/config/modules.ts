/**
 * modules — 前端菜单/路由键的静态镜像（P7-B3 前端切片）。
 *
 * 来源：backend 各域 manifest.py 里声明了 frontend 的 19 个域。
 * 用途：
 *  1. 首屏/降级菜单（后端 /api/modules 不可用时，如生产 4800 重启前）；
 *  2. live 菜单的排序与合法性基准（未知 path 不进菜单，避免死链）；
 *  3. 漂移网：backend/scripts/check_module_menu.py 校验本文件与 manifests 一致，
 *     改后端 manifest 必须同步改这里，否则脚本 exit 1。
 *
 * 注意：/study、/subject-selection、/grad 三个学业聚合页没有后端域认领，
 *  不在这里——它们由 App.tsx 静态路由直接注册（check 脚本报 INFO 允许）。
 */

export interface ModuleMenuItem {
  /** 后端 manifest 声明的目录名，如 "daily_tracker" */
  name: string;
  /** 中文名，如 "日常记录" */
  title: string;
  /** App.tsx <Route path>，如 "/daily" */
  path: string;
  /** menuItems 文案，如 "日常记录" */
  menu: string;
}

/** 顺序 = 当前线上菜单顺序，live 模式也按此排序，保证 UX 零变化。 */
export const FALLBACK_MODULE_MENU: ModuleMenuItem[] = [
  { name: "dashboard", title: "仪表盘", path: "/dashboard", menu: "仪表盘" },
  { name: "daily_tracker", title: "日常记录", path: "/daily", menu: "日常记录" },
  { name: "exam_analyzer", title: "考试分析", path: "/exams", menu: "考试分析" },
  { name: "life_planner", title: "人生目标", path: "/goals", menu: "人生目标" },
  { name: "college", title: "高考志愿", path: "/college", menu: "高考志愿" },
  { name: "career", title: "职业发展", path: "/career", menu: "职业发展" },
  { name: "ai_coach", title: "AI 教练", path: "/ai", menu: "AI 教练" },
  { name: "recommend", title: "智能推荐", path: "/recommend", menu: "智能推荐" },
  { name: "finance", title: "财务", path: "/finance", menu: "财务" },
  { name: "habits", title: "习惯", path: "/habits", menu: "习惯" },
  { name: "health", title: "健康", path: "/health", menu: "健康" },
  { name: "psychology", title: "心理", path: "/psychology", menu: "心理" },
  { name: "family", title: "家庭", path: "/family", menu: "家庭" },
  { name: "interest", title: "兴趣", path: "/interest", menu: "兴趣" },
  { name: "social", title: "社交", path: "/social", menu: "社交" },
  { name: "learning", title: "学习", path: "/learning", menu: "学习" },
  { name: "travel", title: "旅行", path: "/travel", menu: "旅行" },
  { name: "intimacy", title: "亲密", path: "/intimacy", menu: "亲密" },
  { name: "meaning", title: "意义", path: "/meaning", menu: "意义" },
];

/** path → 条目索引，供 live 排序与合法性过滤。 */
export const MODULE_PATH_INDEX: Record<string, number> = Object.fromEntries(
  FALLBACK_MODULE_MENU.map((m, i) => [m.path, i]),
);

/**
 * 无后端域认领的聚合页（P7-B0 check 脚本报 INFO 允许）。
 * 它们没有 manifest，/api/modules 永远不会返回，只能静态注册——
 * 菜单位置保持旧硬编码顺序（/study、/subject-selection 在 /goals 之后；
 * /grad 在 /career 之后），live/fallback 两种模式都追加。
 */
export interface ExtraMenuItem {
  path: string;
  menu: string;
  /** 插在这条已声明 path 之后（旧菜单顺序） */
  after: string;
}

export const EXTRA_MENU: ExtraMenuItem[] = [
  { path: "/study", menu: "学习规划", after: "/goals" },
  { path: "/subject-selection", menu: "选科", after: "/goals" },
  { path: "/grad", menu: "研究生", after: "/career" },
];
