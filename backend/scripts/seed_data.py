"""
Seed data script for Life Planner application.

Usage:
    python scripts/seed_data.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SyncSessionLocal, engine
from models import User, SubjectCombination, CollegeInfo
from sqlalchemy import text
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def seed_subject_combinations(session):
    """
    Seed 12 subject combinations with coverage rates.
    """
    combinations = [
        {"name": "物理+化学+生物", "compulsory_1": "物理", "optional_2": "化学+生物", "coverage_rate": 0.96, "description": "传统理科组合，专业覆盖率最高", "career_directions": "医学、生物工程、化学、材料科学"},
        {"name": "物理+化学+地理", "compulsory_1": "物理", "optional_2": "化学+地理", "coverage_rate": 0.92, "description": "理科+地理，适合理科思维强的学生", "career_directions": "地质、环境、城市规划、气象"},
        {"name": "物理+生物+地理", "compulsory_1": "物理", "optional_2": "生物+地理", "coverage_rate": 0.87, "description": "生物地理组合，适合医学方向", "career_directions": "医学、生物科技、生态学"},
        {"name": "物理+化学+政治", "compulsory_1": "物理", "optional_2": "化学+政治", "coverage_rate": 0.90, "description": "理工+政治，适合考公", "career_directions": "工程、公共管理、法律"},
        {"name": "物理+生物+政治", "compulsory_1": "物理", "optional_2": "生物+政治", "coverage_rate": 0.85, "description": "生物政治组合，适合医学+管理", "career_directions": "医学、公共卫生、健康管理"},
        {"name": "历史+政治+地理", "compulsory_1": "历史", "optional_2": "政治+地理", "coverage_rate": 0.52, "description": "传统文科组合，专业覆盖率较低", "career_directions": "文史、教育、法律、新闻"},
        {"name": "历史+政治+化学", "compulsory_1": "历史", "optional_2": "政治+化学", "coverage_rate": 0.65, "description": "文科+化学，适合医药方向", "career_directions": "药学、中药、公共卫生"},
        {"name": "历史+地理+生物", "compulsory_1": "历史", "optional_2": "地理+生物", "coverage_rate": 0.58, "description": "文史生物组合，适合生态方向", "career_directions": "生态学、环境科学、旅游管理"},
        {"name": "历史+化学+生物", "compulsory_1": "历史", "optional_2": "化学+生物", "coverage_rate": 0.62, "description": "文科+生化，适合医学预科", "career_directions": "基础医学、生物信息学"},
        {"name": "物理+政治+地理", "compulsory_1": "物理", "optional_2": "政治+地理", "coverage_rate": 0.82, "description": "理工+地理政治，适合国土规划", "career_directions": "城市规划、土地管理、应急管理"},
        {"name": "历史+政治+生物", "compulsory_1": "历史", "optional_2": "政治+生物", "coverage_rate": 0.55, "description": "文科+生物政治，适合健康服务", "career_directions": "健康管理、养老服务、社会工作"},
        {"name": "物理+地理+政治", "compulsory_1": "物理", "optional_2": "地理+政治", "coverage_rate": 0.80, "description": "重复，已覆盖", "career_directions": "重复"},
    ]
    
    # Remove duplicate (index 11 is duplicate of 9)
    combinations = combinations[:11]
    
    logger.info(f"Seeding {len(combinations)} subject combinations...")
    
    for combo_data in combinations:
        # Check if already exists
        existing = session.execute(
            text("SELECT id FROM subject_combinations WHERE name = :name"),
            {"name": combo_data["name"]}
        ).fetchone()
        
        if existing:
            logger.info(f"Skipping existing combination: {combo_data['name']}")
            continue
        
        # Insert new combination
        session.execute(
            text("""
                INSERT INTO subject_combinations (name, compulsory_1, optional_2, coverage_rate, description, career_directions, created_at, updated_at, is_deleted)
                VALUES (:name, :compulsory_1, :optional_2, :coverage_rate, :description, :career_directions, :created_at, :updated_at, :is_deleted)
            """),
            {
                "name": combo_data["name"],
                "compulsory_1": combo_data["compulsory_1"],
                "optional_2": combo_data["optional_2"],
                "coverage_rate": combo_data["coverage_rate"],
                "description": combo_data["description"],
                "career_directions": combo_data["career_directions"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_deleted": False,
            }
        )
        logger.info(f"Created combination: {combo_data['name']}")
    
    session.commit()
    logger.info("✅ Subject combinations seeded successfully")


def seed_assessment_questions(session):
    """
    Seed 20 assessment questions (Holland test + ability self-assessment).
    """
    questions = [
        # Holland Interest Test (R/I/A/S/E/C dimensions) - 12 questions
        {"question": "我喜欢动手操作实验器材", "dimension": "R", "type": "holland"},
        {"question": "我对研究自然现象很感兴趣", "dimension": "I", "type": "holland"},
        {"question": "我喜欢创作艺术作品", "dimension": "A", "type": "holland"},
        {"question": "我喜欢帮助他人解决问题", "dimension": "S", "type": "holland"},
        {"question": "我喜欢领导或组织活动", "dimension": "E", "type": "holland"},
        {"question": "我喜欢整理数据和文件", "dimension": "C", "type": "holland"},
        {"question": "我喜欢使用工具修理物品", "dimension": "R", "type": "holland"},
        {"question": "我对科学理论很感兴趣", "dimension": "I", "type": "holland"},
        {"question": "我喜欢表演或展示才艺", "dimension": "A", "type": "holland"},
        {"question": "我喜欢 teaching 他人知识", "dimension": "S", "type": "holland"},
        {"question": "我喜欢销售或推广产品", "dimension": "E", "type": "holland"},
        {"question": "我喜欢按照规则执行任务", "dimension": "C", "type": "holland"},
        # Ability self-assessment - 8 questions
        {"question": "我的数学计算能力很强", "dimension": "math", "type": "ability"},
        {"question": "我的逻辑推理能力很强", "dimension": "logic", "type": "ability"},
        {"question": "我的语言表达能力很强", "dimension": "language", "type": "ability"},
        {"question": "我的空间想象能力很强", "dimension": "spatial", "type": "ability"},
        {"question": "我的记忆能力很强", "dimension": "memory", "type": "ability"},
        {"question": "我的动手能力很强", "dimension": "manual", "type": "ability"},
        {"question": "我的创新能力很强", "dimension": "creativity", "type": "ability"},
        {"question": "我的组织协调能力很强", "dimension": "organization", "type": "ability"},
    ]
    
    logger.info(f"Seeding {len(questions)} assessment questions...")
    
    # For MVP, we store questions in a simple config table or just log them
    # In production, these would be in a database table
    # For now, we'll just print them as they're used in the frontend
    
    logger.info("✅ Assessment questions defined (20 questions)")
    logger.info("Note: Questions are defined in the backend services, not stored in DB for MVP")
    
    # Return questions for reference
    return questions


def seed_knowledge_graph(session):
    """
    Seed knowledge graph data (subject knowledge points).
    """
    knowledge_points = [
        # Math knowledge points
        {"subject": "数学", "point": "函数与导数", "parent": "数学"},
        {"subject": "数学", "point": "立体几何", "parent": "数学"},
        {"subject": "数学", "point": "解析几何", "parent": "数学"},
        {"subject": "数学", "point": "数列与极限", "parent": "数学"},
        {"subject": "数学", "point": "概率与统计", "parent": "数学"},
        # Physics knowledge points
        {"subject": "物理", "point": "力学", "parent": "物理"},
        {"subject": "物理", "point": "电磁学", "parent": "物理"},
        {"subject": "物理", "point": "光学", "parent": "物理"},
        {"subject": "物理", "point": "热学", "parent": "物理"},
        {"subject": "物理", "point": "近代物理", "parent": "物理"},
        # Chemistry knowledge points
        {"subject": "化学", "point": "有机化学", "parent": "化学"},
        {"subject": "化学", "point": "无机化学", "parent": "化学"},
        {"subject": "化学", "point": "物理化学", "parent": "化学"},
        {"subject": "化学", "point": "分析化学", "parent": "化学"},
        # Biology knowledge points
        {"subject": "生物", "point": "细胞生物学", "parent": "生物"},
        {"subject": "生物", "point": "遗传学", "parent": "生物"},
        {"subject": "生物", "point": "生态学", "parent": "生物"},
        {"subject": "生物", "point": "人体生理学", "parent": "生物"},
    ]
    
    logger.info(f"Seeding {len(knowledge_points)} knowledge points...")
    logger.info("✅ Knowledge graph data defined")
    logger.info("Note: Knowledge graph is used in diagnosis reports, not stored separately for MVP")
    
    return knowledge_points


def main():
    """Main entry point for seed data script."""
    logger.info("Starting seed data script...")
    
    # Use sync session for seed data
    session = SyncSessionLocal()
    
    try:
        # Seed subject combinations
        seed_subject_combinations(session)
        
        # Seed assessment questions (returns list for reference)
        questions = seed_assessment_questions(session)
        logger.info(f"Assessment questions: {len(questions)} questions defined")
        
        # Seed knowledge graph
        knowledge_points = seed_knowledge_graph(session)
        logger.info(f"Knowledge points: {len(knowledge_points)} points defined")
        
        session.commit()
        logger.info("✅ Seed data script completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Seed data script failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
