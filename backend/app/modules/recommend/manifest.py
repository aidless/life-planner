"""recommend 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "recommend",
    "title": "智能推荐",
    "router_attr": "router",
    "frontend": {"path": "/recommend", "menu": "智能推荐"},
    "cron": {"schedule": "0 8,21 * * *", "script": "scripts/recommend_push.py"},
}
