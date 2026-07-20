"""
Exam diagnosis prompt template for Life Planner API.

This module defines the prompt template for exam diagnosis.
The prompt is used to ask Claude API to diagnose exam mistakes and provide improvement suggestions.
"""

DIAGNOSIS_PROMPT_TEMPLATE = """你是一位专业的{subject}老师。请对以下试卷进行诊断分析。

试卷信息：
- 试卷名称：{exam_name}
- 科目：{subject}

错题信息：
{wrong_questions}

请对试卷进行诊断分析，包括：
1. 整体分析（overall_analysis）：试卷整体表现评价
2. 优势点（strength_points）：学生表现好的方面
3. 薄弱点（weakness_points）：学生需要改进的方面
4. 知识点漏洞（knowledge_gaps）：具体的知识点漏洞，每个漏洞包括point（知识点名称）和description（描述）
5. 改进建议（improvement_suggestions）：具体的改进建议

请以JSON格式返回结果，格式如下：
{{
  "overall_analysis": "整体分析文字",
  "strength_points": ["优势点1", "优势点2"],
  "weakness_points": ["薄弱点1", "薄弱点2"],
  "knowledge_gaps": [{{"point": "知识点名称", "description": "漏洞描述"}}],
  "improvement_suggestions": ["建议1", "建议2"]
}}

只返回JSON，不要有其他文字。
"""

def build_diagnosis_prompt(
    exam_name: str,
    subject: str,
    wrong_questions_text: str
) -> str:
    """
    Build diagnosis prompt from template.
    
    Args:
        exam_name: Exam name
        subject: Exam subject
        wrong_questions_text: Formatted wrong questions text
        
    Returns:
        str: Formatted prompt
    """
    return DIAGNOSIS_PROMPT_TEMPLATE.format(
        exam_name=exam_name,
        subject=subject,
        wrong_questions=wrong_questions_text
    )


def format_wrong_questions(questions: list) -> str:
    """
    Format wrong questions into text for prompt.
    
    Args:
        questions: List of wrong question dictionaries
        
    Returns:
        str: Formatted text
    """
    if not questions:
        return "本次考试所有题目都答对了，没有错题。\n"
    
    text = ""
    for q in questions:
        text += f"""
题目{q.get('question_number', '?')}：{q.get('question_text', '')}
学生答案：{q.get('student_answer', '')}
正确答案：{q.get('correct_answer', '')}
"""
    
    return text
