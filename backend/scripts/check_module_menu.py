"""一致性校验（P7-B0）：后端 manifests ↔ 前端 App.tsx 路由/菜单。

防 E2E 文件名 22-vs-25 页类漂移重演：
- 每个声明了 frontend 的域：path 必须在 <Route> 里，menu 必须在 menuItems 里；
- 前端有多余路由/菜单（无后端域认领）只报 INFO，不失败
  （/study /scores /predict 等学业页本就跨域聚合）。

用法：./venv/bin/python scripts/check_module_menu.py
退出码：0=一致，1=漂移。
"""
import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import os

os.environ.setdefault(
    "DATABASE_URL", f"sqlite+aiosqlite:///{BACKEND_DIR / 'tests' / 'test_isolated.db'}"
)

from app.modules.loader import discover  # noqa: E402

APP_TSX = BACKEND_DIR.parent / "frontend" / "src" / "App.tsx"


def main() -> int:
    mods = discover()
    print(f"后端域: {len(mods)}")
    src = APP_TSX.read_text(encoding="utf-8")

    route_paths = set(re.findall(r'<Route\s+path="([^"]+)"', src))
    menu_block = re.search(r"const menuItems = \[(.*?)\];", src, re.S)
    menu_keys: set[str] = set()
    menu_labels: set[str] = set()
    if menu_block:
        for m in re.finditer(r"\{\s*key:\s*'([^']+)'\s*,\s*label:\s*<Link to=\"[^\"]*\">([^<]+)</Link>", menu_block.group(1)):
            menu_keys.add(m.group(1))
            menu_labels.add(m.group(2))

    errors: list[str] = []
    for m in mods:
        if not m.frontend_path:
            continue
        if m.frontend_path not in route_paths:
            errors.append(f"路由缺失：域 {m.name} 声明 {m.frontend_path}，App.tsx 无此 <Route>")
        if m.frontend_path not in menu_keys:
            errors.append(f"菜单缺失：域 {m.name} 声明 {m.frontend_path}，menuItems 无此 key")
        if m.frontend_menu and m.frontend_menu not in menu_labels:
            errors.append(f"菜单文案漂移：域 {m.name} 声明 {m.frontend_menu!r}，menuItems 无此文案")

    claimed = {m.frontend_path for m in mods if m.frontend_path}
    for p in sorted(route_paths - claimed - {"/login", "/register", "/", "*"} - {"/colleges", "/colleges/:id"}):
        print(f"INFO 未认领前端路由（跨域聚合页，允许）：{p}")

    if errors:
        print("DRIFT:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"CHECK-OK: {sum(1 for m in mods if m.frontend_path)} 个声明域路由+菜单一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
