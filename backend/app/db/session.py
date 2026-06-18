"""Async SQLAlchemy engine + session factory for the reference-data endpoints."""
from collections.abc import AsyncGenerator
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# asyncpg doesn't accept libpq-style query params like sslmode/channel_binding
# (used by Neon and other managed Postgres hosts) — strip them from the URL
# and translate sslmode=require into the connect_args asyncpg expects instead.
_parsed = urlsplit(settings.async_database_url)
_requires_ssl = "sslmode=require" in _parsed.query
_engine_url = urlunsplit((_parsed.scheme, _parsed.netloc, _parsed.path, "", ""))

engine = create_async_engine(
    _engine_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"ssl": True} if _requires_ssl else {},
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
