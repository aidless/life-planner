"""
Volunteer recommendation prompt template for Life Planner API.

This module defines the prompt template for college volunteer recommendation.
The prompt is used to ask Claude API to recommend colleges based on user's score.
"""

from typing import Optional

VOLUNTEER_PROMPT_TEMPLATE = """你是一位专业的高考志愿填报顾问。请根据以下信息，为学生推荐合适的大学和专业。

学生信息：
- 高考分数：{score}分
- 全省排名：{rank}
- 所在省份：{province}
- 选科组合：{subject_combination}
{target_major_section}

请根据分数和排名，将推荐的大学和专业分为三档：
1. 冲刺档（dash）：分数略高于学生分数，有一定风险但值得冲刺
2. 稳妥档（steady）：分数与学生分数相当，录取概率较大
3. 保底档（safe）：分数低于学生分数，录取概率很高

请以JSON格式返回结果，格式如下：
{{
  "dash": [{{"college_name": "大学名称", "major": "专业名称", "min_score": 最低分数, "probability": "冲刺"}}],
  "steady": [{{"college_name": "大学名称", "major": "专业名称", "min_score": 最低分数, "probability": "稳妥"}}],
  "safe": [{{"college_name": "大学名称", "major": "专业名称", "min_score": 最低分数, "probability": "保底"}}]
}}

只返回JSON，不要有其他文字。
"""

def build_volunteer_prompt(
    score: float,
    rank: str,
    province: str,
    subject_combination: str,
    target_major: Optional[str] = None
) -> str:
    """
    Build volunteer recommendation prompt from template.
    
    Args:
        score: User score
        rank: User rank (string, could be "未知")
        province: User province
        subject_combination: User subject combination
        target_major: Target major (optional)
        
    Returns:
        str: Formatted prompt
    """
    target_major_section = f"- 目标专业：{target_major}\n" if target_major else ""
    
    return VOLUNTEER_PROMPT_TEMPLATE.format(
        score=score,
        rank=rank,
        province=province,
        subject_combination=subject_combination,
        target_major_section=target_major_section
    )
