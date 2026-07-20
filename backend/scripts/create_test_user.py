import asyncio
import sys
sys.path.insert(0, 'F:/life-planner/backend')

from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from database import AsyncSessionLocal, engine
from shared.base_model import Base
import uuid

async def main():
    async with AsyncSessionLocal() as session:
        # 检查是否已有用户
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"Current user count: {count}")

        if count == 0:
            # 创建测试用户
            user_id = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO users (id, phone, password_hash, nickname, is_active, created_at, updated_at)
                VALUES (:id, :phone, :password, :nickname, 1, :created_at, :updated_at)
            """), {
                "id": user_id,
                "phone": "13800138001",
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/Ilu",
                "nickname": "测试用户",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })
            await session.commit()
            print(f"Created test user: {user_id}")
        else:
            result = await session.execute(text("SELECT id, phone, nickname FROM users LIMIT 3"))
            for row in result.fetchall():
                print(f"  User: {row.id} | {row.phone} | {row.nickname}")

if __name__ == "__main__":
    asyncio.run(main())
