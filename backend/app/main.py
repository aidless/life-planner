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

# Import models so Base.metadata knows about all tables
from app.modules.auth.models import User  # noqa: F401
from app.modules.life_planner.models import LifeGoal  # noqa: F401
from app.modules.daily_tracker.models import DailyLog  # noqa: F401
from app.modules.exam_analyzer.models import Exam, ExamQuestion  # noqa: F401
from app.modules.health.models import HealthLog, ExerciseRecord  # noqa: F401
from app.modules.finance.models import Transaction, Budget, FinancialGoal  # noqa: F401
from app.modules.habits.models import Habit, HabitCheckin  # noqa: F401
# W33: 8 个新子域的 models（确保 SQLAlchemy 知道表）
from app.modules.psychology.models import MoodLog, Reflection  # noqa: F401
from app.modules.family.models import FamilyMember, Interaction as FamilyInteraction  # noqa: F401
from app.modules.interest.models import Interest, InterestActivity  # noqa: F401
from app.modules.social.models import Contact, SocialInteraction  # noqa: F401
from app.modules.learning.models import Book, Course  # noqa: F401
from app.modules.travel.models import Trip, BucketList  # noqa: F401
from app.modules.intimacy.models import Relationship, Anniversary  # noqa: F401
from app.modules.meaning.models import Value, LifePurpose  # noqa: F401


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


# Import routers
from app.modules.auth.router import router as auth_router
from app.modules.life_planner.router import router as life_planner_router
from app.modules.daily_tracker.router import router as daily_tracker_router
from app.modules.exam_analyzer.router import router as exam_analyzer_router
from app.modules.ai_coach.router import router as ai_coach_router
# W26: college 模块已重建 (W3 报告虚构的弥补)
from app.modules.college.router import router as college_router
# W32: 3 个 P0 子域（健康/财务/习惯）
from app.modules.health.router import router as health_router
from app.modules.finance.router import router as finance_router
from app.modules.habits.router import router as habits_router
# W38: career module (added fix B-α)
from app.modules.career.router import router as career_router
# W33: 8 个 P1+P2 子域（心理/家庭/兴趣/社交/学习/旅行/亲密/意义）
from app.modules.psychology.router import router as psychology_router
from app.modules.family.router import router as family_router
from app.modules.interest.router import router as interest_router
from app.modules.social.router import router as social_router
from app.modules.learning.router import router as learning_router
from app.modules.travel.router import router as travel_router
from app.modules.intimacy.router import router as intimacy_router
from app.modules.meaning.router import router as meaning_router
# W35: dashboard 模块（聚合 12 维度）
from app.modules.dashboard.router import router as dashboard_router
# W31: import all models so SQLAlchemy create_all builds every table
# (previously only college.models imported, leaving auth/daily_tracker/etc
# tables missing — Bug 13)
from app.modules.college.models import (  # noqa: F401
    CollegeScore, CollegeInfo, ProvinceRank, CollegeRecommendation,
)
from app.modules.auth.models import User  # noqa: F401
from app.modules.life_planner.models import LifeGoal  # noqa: F401
from app.modules.daily_tracker.models import DailyLog  # noqa: F401
from app.modules.exam_analyzer.models import Exam, ExamQuestion  # noqa: F401
from app.modules.health.models import HealthLog, ExerciseRecord  # noqa: F401
from app.modules.finance.models import Transaction, Budget, FinancialGoal  # noqa: F401
from app.modules.habits.models import Habit, HabitCheckin  # noqa: F401
# W33: 8 个新子域的 models（确保 SQLAlchemy 知道表）
from app.modules.psychology.models import MoodLog, Reflection  # noqa: F401
from app.modules.family.models import FamilyMember, Interaction as FamilyInteraction  # noqa: F401
from app.modules.interest.models import Interest, InterestActivity  # noqa: F401
from app.modules.social.models import Contact, SocialInteraction  # noqa: F401
from app.modules.learning.models import Book, Course  # noqa: F401
from app.modules.travel.models import Trip, BucketList  # noqa: F401
from app.modules.intimacy.models import Relationship, Anniversary  # noqa: F401
from app.modules.meaning.models import Value, LifePurpose  # noqa: F401

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

    # Add rate limiting middleware (in-memory; use Redis in production)
    # W36: 调大到 5000 避免 e2e 测试触发（Playwright 23 测试 + 页面请求 ~200）
    app.add_middleware(RateLimitMiddleware, max_requests=5000, window_seconds=60)

    # W38: B4 Trust Boundary middleware (R2.2 case study)
    from app.middleware.trust_bd import TrustBoundaryMiddleware
    app.add_middleware(TrustBoundaryMiddleware)
    
    # W26: college models use the legacy Base (from database.py),
    # so we also create tables for it. Otherwise college tables are
    # missing and college endpoints 500.
    from database import Base as LegacyBase
    LegacyBase.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Register all routers
    app.include_router(auth_router)
    app.include_router(life_planner_router)
    app.include_router(daily_tracker_router)
    app.include_router(exam_analyzer_router)
    app.include_router(ai_coach_router)
    # W3: AI 推荐 - college_router 现在是真实 router (W26 重建)
    if college_router is not None:
        app.include_router(college_router)
    # W32: 3 个 P0 子域
    app.include_router(health_router)
    app.include_router(finance_router)
    app.include_router(habits_router)
    # W38: career (added fix B-α — job applications)
    app.include_router(career_router)
    # W33: 8 个 P1+P2 子域
    app.include_router(psychology_router)
    app.include_router(family_router)
    app.include_router(interest_router)
    app.include_router(social_router)
    app.include_router(learning_router)
    app.include_router(travel_router)
    app.include_router(intimacy_router)
    app.include_router(meaning_router)
    app.include_router(dashboard_router)

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

    return app


app = create_app()
