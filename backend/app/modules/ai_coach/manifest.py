"""ai_coach 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "ai_coach",
    "title": "AI 教练",
    "router_attr": "router",
    "frontend": {"path": "/ai", "menu": "AI 教练"},
    "cron": None,
}
