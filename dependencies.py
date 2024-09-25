from core.database import AsyncSessionLocal
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()