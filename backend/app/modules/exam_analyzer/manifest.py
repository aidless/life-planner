"""exam_analyzer 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "exam_analyzer",
    "title": "考试分析",
    "router_attr": "router",
    "frontend": {"path": "/exams", "menu": "考试分析"},
    "cron": None,
}
