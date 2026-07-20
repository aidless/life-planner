"""AI Coach API router for chat and analysis across all life modules."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import ApiResponse
from app.shared.ai_client import ai_client


class AIChatRequest(BaseModel):
    module: str = Field(
        default="general",
        pattern="^(college|career|study|grad|life|general)$",
    )
    question: str = Field(..., min_length=1, max_length=2000)
    context: str = ""


class AIAnalyzeRequest(BaseModel):
    module: str = Field(
        default="general",
        pattern="^(college|career|study|grad|life|general)$",
    )
    data: str = Field(..., min_length=1)


router = APIRouter(prefix="/api/ai", tags=["ai-coach"])


@router.post("/chat", response_model=ApiResponse)
async def ai_chat(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_user),
):
    answer = await ai_client.chat(payload.module, payload.context, payload.question)
    return ApiResponse(success=True, data={"answer": answer})


@router.post("/analyze", response_model=ApiResponse)
async def ai_analyze(
    payload: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    prompts = {
        "college": "你是高考志愿填报专家，请分析以下数据并给出建议:",
        "career": "你是职业规划师，请分析以下数据并给出建议:",
        "study": "你是学习方法专家，请分析以下数据并给出建议:",
        "grad": "你是研究生导师，请分析以下数据并给出建议:",
        "life": "你是人生规划教练，请分析以下数据并给出建议:",
        "general": "你是全能型AI助手，请分析以下数据并给出建议:",
    }
    system_prompt = prompts.get(payload.module, prompts["general"])
    answer = await ai_client.analyze(system_prompt, payload.data, max_tokens=2048)
    return ApiResponse(success=True, data={"answer": answer})


@router.get("/modules", response_model=ApiResponse)
def list_modules():
    modules = [
        {"key": "life", "name": "人生规划", "desc": "设定和实现人生目标"},
        {"key": "study", "name": "学习规划", "desc": "制定高效的学习计划"},
        {"key": "college", "name": "高考志愿", "desc": "院校和专业选择建议"},
        {"key": "career", "name": "职业发展", "desc": "实习和求职指导"},
        {"key": "grad", "name": "研究生规划", "desc": "选题和申请指导"},
        {"key": "general", "name": "通用咨询", "desc": "各方面的问题咨询"},
    ]
    return ApiResponse(success=True, data=modules)
