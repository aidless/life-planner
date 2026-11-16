# AUTHOR_PATH: F:/life-planner and F:\\life-planner below are the original author's Windows checkout.
# git clone, Docker Compose, and make check do not create that directory.
import asyncio
import sys
sys.path.insert(0, 'F:/life-planner/backend')

from database import AsyncSessionLocal, engine
from sqlalchemy import select, text

async def main():
    async with AsyncSessionLocal() as session:
        # 列出所有用户
        result = await session.execute(text("SELECT id, phone, nickname FROM users LIMIT 5"))
        users = result.fetchall()
        print("Users:")
        for u in users:
            print(f"  {u.id} | {u.phone} | {u.nickname}")

if __name__ == "__main__":
    asyncio.run(main())
