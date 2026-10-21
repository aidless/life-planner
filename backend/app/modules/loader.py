"""Module loader (P7-B0): 发现式加载所有业务域.

替代 main.py 里 20+ 手工 import + include_router。
用法：
    from app.modules.loader import discover
    for mod in discover():
        app.include_router(mod.router)

discover() 只认带 manifest.py 的子目录；__pycache__ 等自动跳过。
models 子模块按副作用导入（与原来 main.py 手工 import models 等价，
保证 Base.metadata.create_all 建全表）。
"""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from typing import Any

import app.modules as _pkg


@dataclass
class ModuleInfo:
    name: str
    title: str
    router: Any
    prefix: str
    frontend_path: str | None = None
    frontend_menu: str | None = None
    cron: dict | None = None


def _iter_module_dirs(package: Any) -> list[str]:
    """直接读目录（不用 pkgutil：ntfs 上曾漏扫 college）。"""
    base = package.__path__[0]
    names: list[str] = []
    for entry in sorted(os.listdir(base)):
        if entry.startswith(("_", ".")):
            continue
        if os.path.isfile(os.path.join(base, entry, "manifest.py")):
            names.append(entry)
    return names


def discover(package: Any = _pkg) -> list[ModuleInfo]:
    """扫描带 manifest.py 的子目录，返回 ModuleInfo 列表（按 name 排序）。"""
    found: list[ModuleInfo] = []
    for name in _iter_module_dirs(package):
        try:
            man_mod = importlib.import_module(f"{package.__name__}.{name}.manifest")
        except ModuleNotFoundError:
            continue  # 无 manifest 的目录：跳过（删域即下线）
        manifest: dict = getattr(man_mod, "MANIFEST")
        assert manifest.get("name") == name, (
            f"manifest name {manifest.get('name')!r} 与目录名 {name!r} 不一致"
        )
        # 副作用导入 models（建表用，与旧 main.py 手工 import 等价）
        try:
            importlib.import_module(f"{package.__name__}.{name}.models")
        except ModuleNotFoundError:
            pass
        router_mod = importlib.import_module(f"{package.__name__}.{name}.router")
        router = getattr(router_mod, manifest.get("router_attr", "router"))
        fe = manifest.get("frontend") or {}
        found.append(
            ModuleInfo(
                name=name,
                title=manifest.get("title", name),
                router=router,
                prefix=getattr(router, "prefix", ""),
                frontend_path=fe.get("path"),
                frontend_menu=fe.get("menu"),
                cron=manifest.get("cron"),
            )
        )
    found.sort(key=lambda m: m.name)
    return found


ARCHIVE_MODULE_NAMES = [
    "finance", "psychology", "family", "social", "intimacy", "travel",
    "meaning", "interest", "health", "habits", "learning",
]


def load_archive_models() -> list[str]:
    """软归档域 models 登记（立意收缩）。

    归档域的路由/菜单/页面已下线，但其 SQLAlchemy models 仍按副作用导入，
    使 Base.metadata.create_all 继续建这些表——与 alembic head 保持列级 parity
    （check_db_drift.py 两路一致），且历史数据不丢、任一步可回滚。
    返回成功导入的归档域名列表。
    """
    loaded: list[str] = []
    for name in ARCHIVE_MODULE_NAMES:
        try:
            importlib.import_module(f"{_pkg.__name__}_archive.{name}.models")
            loaded.append(name)
        except (ModuleNotFoundError, ImportError):
            continue  # 该归档域无 models 或已被物理删除：跳过
    return loaded


def to_api_payload(mods: list[ModuleInfo] | None = None) -> list[dict]:
    """给 GET /api/modules 用的可序列化聚合。"""
    return [
        {
            "name": m.name,
            "title": m.title,
            "api_prefix": m.prefix,
            "frontend_path": m.frontend_path,
            "menu": m.frontend_menu,
            "cron": m.cron,
        }
        for m in (mods if mods is not None else discover())
    ]
