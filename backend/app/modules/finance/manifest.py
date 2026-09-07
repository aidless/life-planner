"""finance 域声明（P7-B0 试点）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "finance",
    "title": "财务",
    "router_attr": "router",
    "frontend": {"path": "/finance", "menu": "财务"},
    "cron": None,
}
