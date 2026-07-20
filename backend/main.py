"""
Life Planner Backend - FastAPI Application Entry Point

This is the main entry point for the Life Planner backend API.
It initializes the FastAPI application, configures middleware,
and registers API routers.

Features:
- FastAPI with OpenAPI documentation
- CORS middleware for frontend integration
- JWT authentication
- SQLAlchemy async database
- Pydantic v2 validation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from contextlib import asynccontextmanager
import logging

from config import settings
from database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Life Planner API...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Life Planner API...")
    await close_db()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-assisted life planning system for high school students",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    Returns basic API information.
    """
    return {
        "code": 200,
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
        },
        "message": "Life Planner API is running",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancer.
    Returns 200 if API is healthy.
    """
    return {
        "code": 200,
        "data": {"status": "healthy"},
        "message": "OK",
    }


# Import and register API routers
from routers.auth import router as auth_router
from routers.subject import router as subject_router
from routers.exams import router as exams_router
from routers.college import router as college_router

app.include_router(auth_router, prefix="/api/auth")
app.include_router(subject_router, prefix="/api/subject")
app.include_router(exams_router, prefix="/api/exams")
app.include_router(college_router, prefix="/api/college")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
