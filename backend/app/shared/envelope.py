"""Response envelope (P7-B2): 锁定既有契约，不发明新格式。

实测契约（前端 client.ts + services/api.ts + Dashboard 在用）：
    成功 {"success": True, "data": {...}}
    失败 HTTPException -> {"detail": ...}；业务失败 -> {"success": False, "error": ...}

注意：frontend/src/types/api.ts 曾写 {code,data,message}，与实际不符，
P7-B2 已按实际修正。新代码用 ok()/fail() 构造，不要手拼字典。
"""

from typing import Any


def ok(data: Any = None) -> dict[str, Any]:
    return {"success": True, "data": data}


def fail(message: str, code: str = "BAD_REQUEST") -> dict[str, Any]:
    return {"success": False, "error": {"code": code, "message": message}}
