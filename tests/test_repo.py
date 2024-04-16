import datetime
import typing as tp
import uuid
from dataclasses import asdict

import pytest

from src.models import ArticleDay, ArticleGood, RegionPublic
from src.repo import Repository
from src.uow import UnitOfWork


@pytest.mark.asyncio
async def test_region_create(
    session_factory: tp.Callable[[], tp.Any], first_region: RegionPublic, second_region: RegionPublic
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)

    async with uow.atomic() as repo:
        await repo.create_region(region=first_region)
        await repo.create_region(region=second_region)

    async with uow.atomic() as repo:
        regions = await repo.get_regions()

    assert regions == [first_region, second_region]


@pytest.mark.asyncio
async def test_article_day_create(
    session_factory: tp.Callable[[], tp.Any], first_region: RegionPublic, second_region: RegionPublic
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)

    first_article_of_day = ArticleDay(
        region=1,
        summary=str(uuid.uuid4()),
        link=str(uuid.uuid4()),
        image_link=str(uuid.uuid4()),
        send_time=datetime.datetime.now(datetime.UTC),
    )
    second_article_of_day = ArticleDay(
        region=1,
        summary=str(uuid.uuid4()),
        link=str(uuid.uuid4()),
        image_link=str(uuid.uuid4()),
        send_time=datetime.datetime.now(datetime.UTC),
    )

    async with uow.atomic() as repo:
        empty_article_of_day = await repo.get_last_article_of_day(region_code=first_region.country_code)

    assert empty_article_of_day is None

    async with uow.atomic() as repo:
        await repo.create_article_of_day(article=first_article_of_day)
        await repo.create_article_of_day(article=second_article_of_day)

    async with uow.atomic() as repo:
        last_article_of_day = await repo.get_last_article_of_day(region_code=first_region.country_code)

    assert last_article_of_day
    assert asdict(last_article_of_day) == asdict(second_article_of_day)


@pytest.mark.asyncio
async def test_article_good_create(
    session_factory: tp.Callable[[], tp.Any], first_region: RegionPublic, second_region: RegionPublic
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)

    first_article_good = ArticleGood(
        region=1,
        summary=str(uuid.uuid4()),
        link=str(uuid.uuid4()),
        image_link=str(uuid.uuid4()),
        send_time=datetime.datetime.now(datetime.UTC),
    )
    second_article_of_good = ArticleGood(
        region=1,
        summary=str(uuid.uuid4()),
        link=str(uuid.uuid4()),
        image_link=str(uuid.uuid4()),
        send_time=datetime.datetime.now(datetime.UTC),
    )

    async with uow.atomic() as repo:
        empty_article_good = await repo.get_last_good_article(region_code=first_region.country_code)

    assert empty_article_good is None

    async with uow.atomic() as repo:
        await repo.create_good_article(article=first_article_good)
        await repo.create_good_article(article=second_article_of_good)

    async with uow.atomic() as repo:
        last_article_good = await repo.get_last_good_article(region_code=first_region.country_code)

    assert last_article_good
    assert asdict(last_article_good) == asdict(second_article_of_good)


@pytest.mark.asyncio
async def test_region_has_id(session_factory: tp.Callable[[], tp.Any], first_region: RegionPublic) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)

    async with uow.atomic() as repo:
        await repo.create_region(region=first_region)

    async with uow.atomic() as repo:
        regions = await repo.get_regions()

    assert regions[0].id
