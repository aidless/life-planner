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

    @staticmethod
    def _rule_daily_feedback(activities: list[dict]) -> str:
        """确定性规则反馈（AI 未启用）：按活动统计产出，数字可复算，非 LLM。"""
        if not activities:
            return "【规则反馈】今天还没有活动记录。先记一条，接入 Claude 后可做深度教练分析。"
        total_min = sum(float(a.get("duration_minutes") or 0) for a in activities)
        by_type: dict[str, float] = {}
        moods: list[float] = []
        energies: list[float] = []
        for a in activities:
            t = str(a.get("activity_type") or "其他")
            by_type[t] = by_type.get(t, 0.0) + float(a.get("duration_minutes") or 0)
            if a.get("mood_level") is not None:
                moods.append(float(a["mood_level"]))
            if a.get("energy_level") is not None:
                energies.append(float(a["energy_level"]))
        top = sorted(by_type.items(), key=lambda kv: kv[1], reverse=True)
        lines = [f"【规则反馈】共记录 {len(activities)} 条活动，合计 {total_min:.0f} 分钟。"]
        for t, m in top[:5]:
            lines.append(f"- {t}：{m:.0f} 分钟")
        if moods:
            lines.append(f"- 平均心情 {sum(moods) / len(moods):.1f}/10")
        if energies:
            lines.append(f"- 平均精力 {sum(energies) / len(energies):.1f}/10")
        if top:
            lines.append(f"投入最多的是「{top[0][0]}」。")
        lines.append("提示：设置 ANTHROPIC_API_KEY 后自动升级为 Claude 深度分析。")
        return "\n".join(lines)

    @staticmethod
    def _rule_exam_analysis(exam_info: dict, questions: list[dict]) -> str:
        """确定性错题分析（AI 未启用）：按知识点/题型聚错，数字可复算。"""
        subject = exam_info.get("subject") or "本场考试"
        wrong = [q for q in questions if not q.get("correct")]
        lines = [f"【规则分析】{subject} 共错 {len(wrong)} 题。"]
        score, full = exam_info.get("score"), exam_info.get("full_score")
        if full and score is not None and float(full) > 0:
            lines.append(f"得分率 {float(score) / float(full) * 100:.1f}%（{score}/{full}）。")
        weak: dict[str, int] = {}
        for q in wrong:
            kp = str(q.get("knowledge_point") or q.get("topic") or "未归类")
            weak[kp] = weak.get(kp, 0) + 1
        for kp, cnt in sorted(weak.items(), key=lambda kv: kv[1], reverse=True)[:5]:
            lines.append(f"- 薄弱点「{kp}」：错 {cnt} 题")
        if wrong:
            lines.append("建议：优先重做上面靠前薄弱点的同类题，再做错题订正。")
        lines.append("提示：设置 ANTHROPIC_API_KEY 后自动升级为 Claude 深度分析。")
        return "\n".join(lines)

    @staticmethod
    def _rule_chat(module: str, question: str) -> str:
        """确定性模板回复（AI 未启用）：热门问题走模板，可复算。"""
        tips = {
            "college": "志愿填报建议：先看全省位次（而非分数），再按冲/稳/保三档各选 3-6 所。",
            "career": "求职准备建议：先明确目标岗位，再倒推补齐技能，简历一页纸突出量化成果。",
            "study": "学习规划建议：用「番茄钟 + 周复盘」，先攻薄弱知识点再刷综合题。",
            "grad": "考研规划建议：先定方向与院校档次，再按公共课/专业课分配时间。",
            "life": "人生目标建议：把大目标拆成季度里程碑，每周末复盘一次进度。",
            "general": "已收到你的问题。接入 Claude 后我可给出针对性分析。",
        }
        head = tips.get(module, tips["general"])
        return (
            f"【规则回复】{head}\n"
            f"（你的问题：「{question[:80]}」）\n"
            "提示：设置 ANTHROPIC_API_KEY 后自动升级为 Claude 深度分析。"
        )

    async def analyze_daily_log(self, activities: list[dict]) -> str:
        """Analyze daily activities and provide feedback."""
        if not self.enabled:
            return self._rule_daily_feedback(activities)
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
        if not self.enabled:
            return self._rule_exam_analysis(exam_info, questions)
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

        if not self.enabled:
            return self._rule_chat(module, question)
        return await self.analyze(system_prompt, user_message, max_tokens=2048)


ai_client = AIClient()
