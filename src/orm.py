import typing as tp

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import registry

from src.models import ArticleDay, ArticleGood, RegionPublic

mapper_registry = registry()


region_table = Table(
    "region",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("country_code", String),
    Column("country", String),
    Column("channel_id", String),
    Column("utc_hour_to_send_day", Integer),
    Column("utc_minute_to_send_day", Integer),
    Column("intervals_for_good_article", String),
    Column("main_page_suffix", String),
    Column("favourite_page_suffix", String),
)

article_day_table = Table(
    "article_day",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("region", String),
    Column("link", String),
    Column("image_link", String),
    Column("summary", String),
    Column("send_time", DateTime(timezone=True), server_default=func.now()),
    Column("title", String, nullable=True),
)

article_good_table = Table(
    "article_good",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("region", String),
    Column("link", String),
    Column("image_link", String),
    Column("summary", String),
    Column("send_time", DateTime(timezone=True), server_default=func.now()),
    Column("title", String, nullable=True),
)


def create_engine(user: str, password: str, host: str, port: str, name: str) -> tp.Callable[[], tp.Any]:
    engine_string = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
    engine = create_async_engine(engine_string, echo=True, pool_size=10, max_overflow=0, pool_timeout=10)
    session_factory: tp.Callable[[], tp.Any] = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory


def start_mappers() -> None:
    mapper_registry.map_imperatively(RegionPublic, region_table)
    mapper_registry.map_imperatively(ArticleDay, article_day_table)
    mapper_registry.map_imperatively(ArticleGood, article_good_table)
