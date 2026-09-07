/**
 * useModules — 动态菜单数据源（P7-B3 前端切片）。
 *
 * 策略：
 *  - 首屏直接用 FALLBACK_MODULE_MENU（与旧硬编码菜单逐项一致，零闪烁、零 UX 变化）；
 *  - 挂载后请求 GET /api/modules（后端 loader.discover() 自声明聚合）；
 *  - live 成功且非空 → 按镜像顺序取交集（未知 path 不进菜单，避免死链；
 *    删域演练时被删域自动从菜单消失，静态 <Route> 保留作深链）；
 *  - 任何失败（404/断网/格式不符，如生产 4800 重启前无此路由）→ 静默保持 fallback。
 *
 * 后端包络 { success, data: { modules, count } }，容忍裸数组以防格式漂移。
 */

import { useEffect, useState } from "react";
import apiClient from "@/api/client";
import {
  EXTRA_MENU,
  FALLBACK_MODULE_MENU,
  MODULE_PATH_INDEX,
  type ModuleMenuItem,
} from "@/config/modules";

export interface MenuEntry {
  key: string;
  label: string;
}

export type MenuSource = "fallback" | "live";

interface LiveModule {
  name?: string;
  title?: string;
  frontend_path?: string | null;
  menu?: string | null;
}

/** fallback 首屏：19 声明域 + 3 聚合页，按旧硬编码顺序交错。 */
function fallbackEntries(): MenuEntry[] {
  const items: MenuEntry[] = [];
  for (const m of FALLBACK_MODULE_MENU) {
    items.push({ key: m.path, label: m.menu });
    for (const e of EXTRA_MENU.filter((x) => x.after === m.path)) {
      items.push({ key: e.path, label: e.menu });
    }
  }
  return items;
}
/** live 转菜单：按镜像顺序取交集 + 追加 3 聚合页（旧顺序）；未知 path 丢弃。 */
function toMenuItems(live: LiveModule[]): MenuEntry[] | null {
  const known = live.filter(
    (m): m is LiveModule & { frontend_path: string } =>
      typeof m.frontend_path === "string" && m.frontend_path in MODULE_PATH_INDEX,
  );
  if (known.length === 0) return null;
  const mapped: MenuEntry[] = known
    .slice()
    .sort(
      (a, b) =>
        MODULE_PATH_INDEX[a.frontend_path] - MODULE_PATH_INDEX[b.frontend_path],
    )
    .map((m) => ({
      key: m.frontend_path,
      // 文案优先用后端自声明（与 manifest.menu 同源），缺失才回镜像
      label:
        m.menu ??
        FALLBACK_MODULE_MENU[MODULE_PATH_INDEX[m.frontend_path]].menu,
    }));
  // 交错追加 3 聚合页，保持旧菜单顺序
  const items: MenuEntry[] = [];
  for (const d of FALLBACK_MODULE_MENU) {
    const hit = mapped.find((x) => x.key === d.path);
    if (hit) items.push(hit);
    for (const e of EXTRA_MENU.filter((x) => x.after === d.path)) {
      items.push({ key: e.path, label: e.menu });
    }
  }
  return items;
}

export function useModules() {
  const [menuItems, setMenuItems] = useState<MenuEntry[]>(() =>
    fallbackEntries(),
  );
  const [source, setSource] = useState<MenuSource>("fallback");

  useEffect(() => {
    let cancelled = false;
    apiClient
      .get("/modules")
      .then((res) => {
        if (cancelled) return;
        const body = res.data as unknown;
        const arr: unknown =
          (body as { data?: { modules?: unknown } })?.data?.modules ?? body;
        if (!Array.isArray(arr)) return;
        const items = toMenuItems(arr as LiveModule[]);
        if (items) {
          setMenuItems(items);
          setSource("live");
        }
      })
      .catch(() => {
        // 静默降级：保持 fallback（生产 4800 重启前 /api/modules 尚不存在）
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { menuItems, source };
}

export type { ModuleMenuItem };
