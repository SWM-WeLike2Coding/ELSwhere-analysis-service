from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=int(os.getenv('DATABASE_POOL_SIZE')),
    max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW'))
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()