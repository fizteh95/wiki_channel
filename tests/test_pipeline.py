import asyncio
import datetime
import time
import typing as tp
import uuid
from dataclasses import asdict

import pytest
from tests.conftest import MockSender

from src.models import ArticleDay, ArticleGood, RegionPublic
from src.pipeline import ArticleFlow
from src.repo import Repository
from src.scraper import Scraper
from src.uow import UnitOfWork


async def stopper(seconds: float, af: ArticleFlow) -> None:
    await asyncio.sleep(seconds)
    af.ag_loop = False
    af.ad_loop = False


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 12:00:01", tick=True)
async def test_article_day_loop_empty(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    async with uow.atomic() as repo:
        await repo.create_region(region=first_region)
    sender = MockSender()
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)
    await asyncio.gather(*[stopper(seconds=5, af=af), af.article_day_loop()])
    assert len(list(filter(lambda x: isinstance(x, ArticleDay), sender.sent))) == 1


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 12:00:01", tick=True)
async def test_article_day_loop_not_empty(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    async with uow.atomic() as repo:
        await repo.create_region(region=first_region)

    article_day = await Scraper().get_article_of_day(region=first_region)
    async with uow.atomic() as repo:
        article_day.link = str(uuid.uuid4())
        await repo.create_article_of_day(article=article_day)

    sender = MockSender()
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)
    await asyncio.gather(*[stopper(seconds=5, af=af), af.article_day_loop()])
    assert len(list(filter(lambda x: isinstance(x, ArticleDay), sender.sent))) == 1


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 12:00:01", tick=True)
async def test_article_day_loop_not_empty_old_article(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    async with uow.atomic() as repo:
        await repo.create_region(region=first_region)

    article_day = await Scraper().get_article_of_day(region=first_region)
    async with uow.atomic() as repo:
        await repo.create_article_of_day(article=article_day)

    sender = MockSender()
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)
    await asyncio.gather(*[stopper(seconds=5, af=af), af.article_day_loop()])
    assert len(list(filter(lambda x: isinstance(x, ArticleDay), sender.sent))) == 0
