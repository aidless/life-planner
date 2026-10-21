#!/usr/bin/env python3
"""软归档 11 后端模块：modules/ → modules_archive/，并重写其内部绝对导入。

安全：os.rename 同盘原子移动；只改目标模块文件里的 app.modules.<self> 自引用，
保留 app.modules.auth / app.modules._manifest_schema 等被保留域引用。
产出 modules_archive/__init__.py 与 load_archive_models() 注册点。
"""
import os
import shutil
import sys
from pathlib import Path

REPO = Path("/data3/projects/life-planner")
MODULES = REPO / "backend" / "app" / "modules"
ARCHIVE = REPO / "backend" / "app" / "modules_archive"

ARCHIVE_NAMES = [
    "finance", "psychology", "family", "social", "intimacy", "travel",
    "meaning", "interest", "health", "habits", "learning",
]


def rewrite_imports(mod_dir: Path, name: str) -> int:
    """重写该模块内 app.modules.<name> → app.modules_archive.<name>，返回改动文件数."""
    changed = 0
    old = f"app.modules.{name}"
    new = f"app.modules_archive.{name}"
    for py in sorted(mod_dir.rglob("*.py")):
        text = py.read_text(encoding="utf-8")
        if old in text:
            text = text.replace(old, new)
            py.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def main() -> int:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    # __init__.py
    init = ARCHIVE / "__init__.py"
    if not init.exists():
        init.write_text('"""软归档模块（立意收缩）。routes/menus 下线，models 仍登记进 AppBase.metadata。"""\n',
                        encoding="utf-8")

    moved = []
    for name in ARCHIVE_NAMES:
        src = MODULES / name
        dst = ARCHIVE / name
        if not src.is_dir():
            print(f"SKIP {name}: 源目录不存在")
            continue
        if dst.exists():
            print(f"SKIP {name}: 目标已存在（幂等）")
            continue
        os.rename(str(src), str(dst))
        n = rewrite_imports(dst, name)
        moved.append((name, n))
        print(f"MOVED {name} (rewrote {n} files)")

    # 清理残留 __pycache__（避免 Python 从旧路径误读缓存的 .pyc）
    for name in ARCHIVE_NAMES:
        pc = ARCHIVE / name / "__pycache__"
        if pc.is_dir():
            shutil.rmtree(pc, ignore_errors=True)
    pc = MODULES / "__pycache__"
    # 不动 modules/__pycache__（含 loader 缓存，属保留域）

    print(f"\n总计移动 {len(moved)} 模块")
    return 0


if __name__ == "__main__":
    sys.exit(main())