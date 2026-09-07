"""一致性校验（P7-B0 建，P7-B3 改）：后端 manifests ↔ 前端路由/菜单。

防 E2E 文件名 22-vs-25 页类漂移重演：
- 每个声明了 frontend 的域：path 必须在 App.tsx <Route> 里；
- menu 来源（P7-B3 后）：首屏/降级菜单 = config/modules.ts 静态镜像
  + EXTRA_MENU（3 聚合页），live 菜单 = /api/modules 自声明聚合。
  本脚本校验：manifests ↔ 静态镜像三元组一致，且 App.tsx 仍消费 useModules；
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
    # P7-B3：菜单不再硬编码于 App.tsx（改走 useModules + 静态镜像）。
    # App.tsx 侧只断言仍在消费 useModules；菜单键/文案断言改走镜像。
    if "useModules()" not in src:
        errors: list[str] = ["App.tsx 未消费 useModules（P7-B3 动态菜单被绕过？）"]
    else:
        errors = []
    menu_keys, menu_labels = _read_menu_sources()
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

    # P7-B3: 静态镜像校验（frontend/src/config/modules.ts 必须与 manifests 同步，
    # 否则首屏/降级菜单漂移）。解析 { name, path, menu } 三元组 + EXTRA_MENU。
    errors.extend(_check_mirror(mods))

    if errors:
        print("DRIFT:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"CHECK-OK: {sum(1 for m in mods if m.frontend_path)} 个声明域路由+菜单一致")
    return 0


def _read_menu_sources() -> tuple[set[str], set[str]]:
    """读前端菜单两来源：静态镜像三元组 + EXTRA_MENU（P7-B3）。"""
    mirror = BACKEND_DIR.parent / "frontend" / "src" / "config" / "modules.ts"
    src = mirror.read_text(encoding="utf-8")
    keys = set(m[1] for m in re.findall(
        r'\{\s*name:\s*"([^"]+)"\s*,\s*title:\s*"[^"]*"\s*,\s*path:\s*"([^"]+)"\s*,\s*menu:\s*"([^"]+)"\s*\}',
        src,
    ))
    labels = set(m[2] for m in re.findall(
        r'\{\s*name:\s*"([^"]+)"\s*,\s*title:\s*"[^"]*"\s*,\s*path:\s*"([^"]+)"\s*,\s*menu:\s*"([^"]+)"\s*\}',
        src,
    ))
    for path, menu in re.findall(
        r'\{\s*path:\s*"([^"]+)"\s*,\s*menu:\s*"([^"]+)"\s*,\s*after:',
        src,
    ):
        keys.add(path)
        labels.add(menu)
    return keys, labels


def _check_mirror(mods) -> list[str]:
    """校验 config/modules.ts 镜像与 manifests 一致（P7-B3 漂移网第二道）。"""
    errors: list[str] = []
    mirror = BACKEND_DIR.parent / "frontend" / "src" / "config" / "modules.ts"
    if not mirror.is_file():
        return ["镜像缺失：frontend/src/config/modules.ts 不存在"]
    src = mirror.read_text(encoding="utf-8")
    mirrored = set(
        re.findall(
            r'\{\s*name:\s*"([^"]+)"\s*,\s*title:\s*"[^"]*"\s*,\s*path:\s*"([^"]+)"\s*,\s*menu:\s*"([^"]+)"\s*\}',
            src,
        )
    )
    expected = {
        (m.name, m.frontend_path, m.frontend_menu)
        for m in mods
        if m.frontend_path
    }
    for name, path, menu in sorted(expected - mirrored):
        errors.append(f"镜像缺失：域 {name}（{path}/{menu}）未同步到 config/modules.ts")
    for name, path, menu in sorted(mirrored - expected):
        errors.append(f"镜像残留：config/modules.ts 有 ({name},{path},{menu}），后端无此声明")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
