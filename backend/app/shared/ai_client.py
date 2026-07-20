"""Claude API client for AI-powered analysis and recommendations."""

import json
from typing import Optional

from anthropic import Anthropic
from sqlalchemy.orm import Session

from app.config import get_settings
from app.shared.context import build_user_summary, inject_user_context


class AIClient:
    """Wrapper around Anthropic Claude API for life planning analysis.

    Added 2026-07-19 fix C: chat() now accepts optional db and user_id,
    auto-injecting recent daily_logs context into the prompt.
    """

    def __init__(self):
        settings = get_settings()
        api_key = settings.ANTHROPIC_API_KEY
        self.client = Anthropic(api_key=api_key) if api_key else None
        self.model = settings.AI_MODEL
        self.enabled = bool(api_key)

    async def analyze(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
    ) -> str:
        """Send a message to Claude and return the response text."""
        if not self.enabled:
            return "AI 分析服务未配置（缺少 ANTHROPIC_API_KEY）"

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text
        except Exception as e:
            return f"AI 分析请求失败: {str(e)}"

    async def analyze_daily_log(self, activities: list[dict]) -> str:
        """Analyze daily activities and provide feedback."""
        system_prompt = (
            "你是一位专业的人生规划教练。分析用户的日常活动记录，"
            "给出建设性反馈和改进建议。用中文回复，保持积极鼓励的语气。"
        )
        user_message = (
            "以下是我今天的活动记录，请分析:\n"
            + json.dumps(activities, ensure_ascii=False, indent=2)
        )
        return await self.analyze(system_prompt, user_message)

    async def analyze_exam(
        self, exam_info: dict, questions: list[dict]
    ) -> str:
        """Analyze exam results and provide study recommendations."""
        system_prompt = (
            "你是一位经验丰富的教育分析师。分析学生的考试表现，"
            "识别知识薄弱点，给出针对性的学习建议。用中文回复。"
        )
        user_message = (
            f"考试信息:\n{json.dumps(exam_info, ensure_ascii=False, indent=2)}\n\n"
            f"错题分析:\n{json.dumps(questions, ensure_ascii=False, indent=2)}"
        )
        return await self.analyze(system_prompt, user_message, max_tokens=2048)

    async def chat(
        self,
        module: str,
        context: str,
        question: str,
        *,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        return_prompt: bool = False,
    ) -> str:
        """General AI chat for any module.

        Added fix C: when db + user_id provided, automatically injects
        recent daily_logs (last 7 days) into the system prompt so
        coach knows user's recent context.

        If return_prompt=True, returns the constructed (system, user) prompt
        instead of calling LLM — useful for testing prompt logic.

        Returns graceful fallback strings when AI not configured.
        """
        prompts = {
            "college": "你是高考志愿填报专家，根据学生分数、兴趣和职业规划提供建议。",
            "career": "你是职业规划师，帮助应届生和在校生规划实习和求职。",
            "study": "你是学习方法专家，帮助制定高效的学习计划。",
            "grad": "你是研究生导师，帮助选择研究方向和申请学校。",
            "life": "你是人生规划教练，帮助设定和实现人生目标。",
            "general": "你是全能型AI助手，帮助用户解决人生各阶段的问题。",
        }
        system_prompt = prompts.get(module, prompts["general"])

        # Inject user context if available (fix C)
        user_summary_text = ""
        if db is not None and user_id is not None:
            try:
                user_summary_text = build_user_summary(db, int(user_id), days=7)
                if user_summary_text:
                    system_prompt = inject_user_context(system_prompt, user_summary_text)
            except Exception as e:
                # don't break chat if context fetch fails
                import logging
                logging.warning(f"Failed to build user summary: {e}")

        # Include explicit context if user passed one
        user_message = question
        if context:
            user_message = f"[上下文: {context}]\n\n{question}"

        if return_prompt:
            return (system_prompt, user_message)

        return await self.analyze(system_prompt, user_message, max_tokens=2048)


ai_client = AIClient()
