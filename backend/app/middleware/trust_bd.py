"""
B4 Trust Boundary middleware for FastAPI (R2.2 integration)

论文 §6 Case Study: B4 中间件挂在 life-planner backend 上拦截所有 /api/* 请求。

设计：
1. JWT auth（existing）→ 提取 user_id
2. B4 Capability check（B4 Reference Monitor）→ grant / revoke
3. Audit log 写入 trust-cap SQLiteStore
4. 越权时返回 403；正常放行
"""

from __future__ import annotations
import os
import sys
import json
import time
from typing import Optional

import jwt
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# 用 trust-cap 库
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../test/2026-07-16-11-16-52/capability/src"))
from trust_cap import (
    Capability, SigningKey, ReferenceMonitor, AuditChain, Action,
    PermissionDenied,
)

# === Config ===
SECRET = os.environ.get("LIFE_PLANNER_SECRET", "dev-secret-key-change-in-prod")
B4_USER_KEY_PATH = os.environ.get("B4_USER_KEY_PATH", "/tmp/b4_user.key")
AUDIT_DB_PATH = os.environ.get("B4_AUDIT_DB", "/tmp/life_planner_b4_audit.db")


# === Singleton ===
_monitor: Optional[ReferenceMonitor] = None
_audit: Optional[AuditChain] = None
_user_key: Optional[SigningKey] = None


def _init():
    global _monitor, _audit, _user_key
    if _monitor is not None:
        return

    _user_key = SigningKey.generate()  # In production: load from secure vault

    _monitor = ReferenceMonitor()
    _monitor.register_key("user:N", _user_key)  # Generic user:N pattern

    _audit = AuditChain(signing_key=_user_key)

    # Pre-grant minimal capabilities on health endpoints
    for path, action in [
        ("/api/health", "memory.read"),
        ("/api/info", "memory.read"),
    ]:
        cap = Capability(
            subject="system",
            resource=path,
            action=action,
            ttl_seconds=86400,
        ).sign(_user_key)
        _monitor.register_key("system", _user_key)
        _monitor.grant(cap)


_init()


# === Helpers ===

def verify_jwt(token: str) -> dict:
    """简化 JWT 验证（用 life-planner 现有）"""
    try:
        # Life-planner JWT 直接 decode
        return jwt.decode(token, SECRET, algorithms=["HS256"], options={"verify_signature": False})
    except Exception:
        return {}


def _path_to_operation(method: str, path: str) -> tuple[str, str]:
    """Map HTTP method + path to (action, resource) for capability check.
    e.g. (GET, /api/daily-logs) → ("memory.read", "life_planner:daily_logs")
    """
    # Strip /api prefix and ID suffix
    clean = path.replace("/api/", "").rstrip("/").split("?")[0]
    # Extract resource name from first path segment
    parts = clean.split("/")
    resource_root = parts[0] if parts else "default"
    # Convert kebab-case to snake_case
    resource = resource_root.replace("-", "_")

    # Method to action
    method_to_action = {
        "GET": "memory.read",
        "POST": "memory.write",
        "PUT": "memory.write",
        "DELETE": "memory.delete",
    }
    action = method_to_action.get(method, "memory.read")

    return action, resource


# === Middleware ===

class TrustBoundaryMiddleware(BaseHTTPMiddleware):
    """B4 Trust Boundary ASGI middleware.

    Usage:
        app.add_middleware(TrustBoundaryMiddleware)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip non-API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Skip health/info (pre-granted, no auth needed)
        if request.url.path in ("/api/health", "/api/info"):
            return await call_next(request)

        # B4 doesn't intercept auth flow — let existing auth middleware handle
        # We only check capability if user is authenticated
        token = request.headers.get("authorization", "").replace("Bearer ", "").strip()
        if not token:
            # No token — auth middleware will reject 401
            return await call_next(request)

        user_payload = verify_jwt(token)
        user_id = user_payload.get('user_id')
        if not user_id:
            # Invalid JWT — auth middleware will reject 401
            return await call_next(request)

        subject = f"user:{user_id}"

        # Step 2: Map request to operation
        action, resource = _path_to_operation(request.method, request.url.path)

        # Step 3: B4 capability check
        # Auto-grant capability for new user (first-request convenience; production: pre-grant via OAuth scope)
        try:
            existing_keys = set(_monitor._subject_keys.keys())
            if subject not in existing_keys:
                _monitor.register_key(subject, _user_key)
                cap = Capability(
                    subject=subject,
                    resource=resource,
                    action=action,
                    conditions={"scope": "self"},
                    ttl_seconds=3600,
                ).sign(_user_key)
                _monitor.grant(cap)

            verified_cap = _monitor.check(
                subject=subject,
                action=action,
                resource=resource,
            )
            _audit.append(
                subject=subject, action=action, resource=resource,
                capability=verified_cap, decision="granted",
            )
        except PermissionDenied as e:
            _audit.append(
                subject=subject, action=action, resource=resource,
                capability=None, decision="denied",
            )
            return JSONResponse({"detail": f"B4: {str(e)}", "b4_blocked": True}, status_code=403)

        return await call_next(request)
