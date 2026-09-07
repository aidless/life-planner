"""life_planner 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "life_planner",
    "title": "人生目标",
    "router_attr": "router",
    "frontend": {"path": "/goals", "menu": "人生目标"},
    "cron": None,
}
