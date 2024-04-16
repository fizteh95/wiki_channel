import asyncio
import datetime
import typing as tp
import uuid

import pytest
import settings

from src.models import RegionPublic
from src.orm import create_engine, start_mappers


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


@pytest.fixture(scope="package")
def first_region() -> RegionPublic:
    region = RegionPublic(
        country_code=str(uuid.uuid4()),
        country=str(uuid.uuid4()),
        channel_id=str(uuid.uuid4()),
        utc_hour_to_send_day=10,
        utc_minute_to_send_day=20,
        interval_for_goof_article=30,
        main_page_suffix="ru"
    )
    region.id = 1
    return region


@pytest.fixture(scope="package")
def second_region() -> RegionPublic:
    region = RegionPublic(
        country_code=str(uuid.uuid4()),
        country=str(uuid.uuid4()),
        channel_id=str(uuid.uuid4()),
        utc_hour_to_send_day=9,
        utc_minute_to_send_day=45,
        interval_for_goof_article=15,
        main_page_suffix="en"
    )
    region.id = 2
    return region
