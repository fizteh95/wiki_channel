import asyncio
import datetime
import typing as tp
import uuid

import pytest
import pytest_asyncio
import settings

from src.models import Article, RegionPublic
from src.orm import create_engine, start_mappers
from src.pipeline import AbstractSender
from src.repo import Repository
from src.uow import UnitOfWork


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def session_factory(event_loop: asyncio.BaseEventLoop) -> tp.Callable[[], tp.Any]:
    start_mappers()
    factory = create_engine(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        name=settings.DB_NAME,
    )
    return factory


@pytest_asyncio.fixture(scope="function")
async def remove_old_data(session_factory: tp.Callable[[], tp.Any]) -> tp.Any:
    # yield
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    async with uow.atomic() as repo:
        await repo.remove_all()
    return


@pytest.fixture  # (scope="package")
def first_region() -> RegionPublic:
    region = RegionPublic(
        country_code="ru",
        country=str(uuid.uuid4()),
        channel_id=str(uuid.uuid4()),
        utc_hour_to_send_day=10,
        utc_minute_to_send_day=20,
        interval_for_goof_article=30,
        main_page_suffix="Заглавная_страница",
        favourite_page_suffix="Википедия:Избранные_статьи",
    )
    # region.id = 1
    return region


@pytest.fixture  # (scope="package")
def second_region() -> RegionPublic:
    region = RegionPublic(
        country_code=str(uuid.uuid4()),
        country=str(uuid.uuid4()),
        channel_id=str(uuid.uuid4()),
        utc_hour_to_send_day=12,
        utc_minute_to_send_day=00,
        interval_for_goof_article=15,
        main_page_suffix="en",
        favourite_page_suffix="1123",
    )
    # region.id = 2
    return region


class MockSender(AbstractSender):
    def __init__(self) -> None:
        self.sent: list[Article] = []

    async def send_article(self, article: Article, region_channel: str) -> None:
        self.sent.append(article)
        return None
