"""Module manifest schema (P7-B0 模块化单体).

每个业务域在自己目录下放一个 manifest.py，声明：
  MANIFEST = {
    "name": "<目录名，必须一致>",
    "title": "<中文名，用于 /api/modules 与管理面>",
    "router_attr": "router",          # router.py 里暴露的 APIRouter 变量名
    "frontend": {                     # 可选：有对应前端页面的域才填
        "path": "/health",            # App.tsx <Route path>
        "menu": "健康",               # App.tsx menuItems 文案
    },
    "cron": None,                     # 可选：{"schedule": "0 8,21 * * *", "script": "xxx.py"}
  }

main.py 不再手写 20 个 import，改为 loader.discover() 发现式加载。
删域 = 删目录（或删 manifest.py），服务照常启动，/api/modules 自动除名。
"""

from typing import TypedDict


class FrontendDecl(TypedDict, total=False):
    path: str
    menu: str


class CronDecl(TypedDict):
    schedule: str
    script: str


class Manifest(TypedDict, total=False):
    name: str
    title: str
    router_attr: str
    frontend: FrontendDecl
    cron: CronDecl | None
