from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config.config import database_url


Base = declarative_base()
if not database_url:
    raise RuntimeError("Database URL не задан.")

engine = create_async_engine(database_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncSession:
    session = AsyncSessionLocal()

    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()