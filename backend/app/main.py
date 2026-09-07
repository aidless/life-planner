"""FastAPI application entry point.

人生规划系统 (Life Planner) — AI 驱动的人生规划系统。
入口文件，所有 router 在这里注册。
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import get_settings
from app.database import engine
from app.shared.base_model import Base

# P7-B0: models 不再这里手写 import —— loader.discover() 在 create_app 内
# 按副作用导入各域 models（先于 create_all），与旧手工 import 等价。


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.
    
    按客户端 IP 在 60s 窗口内限制请求数。生产环境应换为 Redis 实现。
    """
    
    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def reset(self) -> None:
        """Clear all rate-limit state. Useful for tests."""
        self.request_counts.clear()

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        """处理请求 + 检查限流。
        
        Args:
            request: Starlette 请求对象
            call_next: 下一个 ASGI 应用
            
        Returns:
            Response 对象
        """
        client_ip: str = request.client.host if request.client else "unknown"
        now = datetime.now()
        
        async with self._lock:
            # Clean old requests
            window_start = now - timedelta(seconds=self.window_seconds)
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if req_time > window_start
            ]
            
            # Check rate limit
            if len(self.request_counts[client_ip]) >= self.max_requests:
                # W29.2: return the standard error envelope so clients
                # can parse {success, error, ...} uniformly
                return Response(
                    content='{"success":false,"error":"Rate limit exceeded","detail":"Too many requests"}',
                    status_code=429,
                    media_type="application/json",
                )
            
            # Add current request
            self.request_counts[client_ip].append(now)
        
        response = await call_next(request)
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """P7-B2: 可观测追踪 — 透传/生成 X-Request-ID，全响应携带。

    加法变更：不碰业务包络（{success,data} 锁死，见 app/shared/envelope.py），
    只加响应头，方便把前端报错和后端日志对上。
    """

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        import uuid

        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response


# P7-B0: 发现式加载（替代 20+ 手工 import + include_router）。
# 每个域靠自家 manifest.py 自声明；删域 = 删目录，服务照常启动。
# router 前缀清单见各 manifest；loader 干跑校验见 scripts/check_module_menu.py。
from app.modules.loader import discover as _discover_modules
from app.modules.loader import to_api_payload as _modules_payload

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        配置完成的 FastAPI app 实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="AI 驱动的人生规划系统 - Life Planning System",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add rate limiting middleware (in-memory; use Redis in production).
    # 换 Redis 的触发阈值（P7-B2 明确化）：单实例 429 率连续 1 天 >1% 才换，
    # 未到阈值不动——当前 e2e/生产从未触发。
    # W36: 调大到 5000 避免 e2e 测试触发（Playwright 23 测试 + 页面请求 ~200）
    app.add_middleware(RateLimitMiddleware, max_requests=5000, window_seconds=60)

    # P7-B2: 请求追踪（加法，业务零改动）
    app.add_middleware(RequestIdMiddleware)

    # W38: B4 Trust Boundary middleware (R2.2 case study)
    from app.middleware.trust_bd import TrustBoundaryMiddleware
    app.add_middleware(TrustBoundaryMiddleware)
    
    # P7-B0: 发现式加载全部域（models 副作用导入先于 create_all，
    # 等价于旧手工 import models；router 逐个挂载）。
    # P1-fix 语义保留：Base 先建占 users 表，Legacy 后建、重名跳过。
    from database import Base as LegacyBase
    _modules = _discover_modules()
    Base.metadata.create_all(bind=engine)
    LegacyBase.metadata.create_all(bind=engine)

    # Register all routers (discovered)
    for _mod in _modules:
        app.include_router(_mod.router)
    app.state.modules = _modules

    @app.get("/api/health")
    def health_check() -> dict[str, Any]:
        """健康检查端点 — 用于监控。"""
        return {"success": True, "data": {"status": "healthy"}}

    @app.get("/api/info")
    def info() -> dict[str, Any]:
        """服务信息 — 版本/启动时间/路由统计。"""
        from app.shared.base_model import Base  # noqa: PLC0415
        from app.database import engine  # noqa: PLC0415
        insp = engine.dialect.get_columns if hasattr(engine.dialect, "get_columns") else None
        try:
            from sqlalchemy import inspect  # noqa: PLC0415
            tables = inspect(engine).get_table_names()
        except Exception:
            tables = []
        return {
            "success": True,
            "data": {
                "name": "LifePlanner",
                "version": "0.1.0",
                "tables_count": len(tables),
                "tables": tables,
            },
        }

    @app.get("/api/modules")
    def list_modules(request: Request) -> dict[str, Any]:
        """已加载业务域聚合（P7-B0 自声明 manifests）— 供前端菜单校验与管理面。"""
        mods = getattr(request.app.state, "modules", None)
        payload = _modules_payload(mods) if mods is not None else _modules_payload()
        return {"success": True, "data": {"modules": payload, "count": len(payload)}}

    # P2-1: 同源 serving 前端 SPA（frontend/dist）。
    # 背景：vite proxy 只在 dev 生效，生产 serve(8080) 下 /api 相对路径 404，
    # 所有页面调数失败。改由后端 8001 同源托管 dist，/api 直通，无需代理/CORS。
    from pathlib import Path  # noqa: PLC0415
    _DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if _DIST.is_dir():
        from fastapi.responses import FileResponse  # noqa: PLC0415
        from fastapi.staticfiles import StaticFiles  # noqa: PLC0415

        _assets = _DIST / "assets"
        if _assets.is_dir():
            app.mount("/assets", StaticFiles(directory=str(_assets)), name="spa-assets")

        @app.get("/", include_in_schema=False)
        def spa_root() -> FileResponse:
            return FileResponse(str(_DIST / "index.html"))

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa_fallback(full_path: str) -> FileResponse:
            from fastapi import HTTPException  # noqa: PLC0415
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not Found")
            fp = _DIST / full_path
            if fp.is_file():
                return FileResponse(str(fp))
            return FileResponse(str(_DIST / "index.html"))

    return app


app = create_app()
