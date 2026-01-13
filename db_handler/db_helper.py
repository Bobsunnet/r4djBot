from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings


class DatabaseHelper:
    def __init__(self):
        self.engine = create_async_engine(
            url=settings.db.db_url,
            echo=settings.db.echo,
        )
        self.session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session_getter(self) -> AsyncSession:
        session = self.session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


db_helper = DatabaseHelper()
