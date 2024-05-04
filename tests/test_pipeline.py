import asyncio
import datetime
import time
import typing as tp
import uuid
from dataclasses import asdict

import pytest
from tests.conftest import MockSender

from src.models import Article, ArticleDay, ArticleGood, RegionPublic
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


@pytest.mark.asyncio
async def test_article_prune() -> None:
    text = (
        "Считается одним из лучших нападающих в мире[4][5][6]. "
        "Кавалер Командорского креста ордена Возрождения Польши[79]. "
        "«Бе́шеные псы»[~ 1] (англ. Reservoir Dogs) — дебютный[~ 2] фильм. "
        "в составе сборника на платформе iOS[⇨]. итальянский 3D-анимированный "
        "Rainbow CGI[K 1] совместно с Rai Fictionruen, "
        "Евге́ний Петро́вич Петро́в (настоящая фамилия — Катаев; 30 ноября "
        "[13 декабря] 1902, Одесса"
    )
    article = Article(
        region="ru",
        summary=text,
        link="https://example.com",
        image_link="https://example.com",
        send_time=datetime.datetime.now(datetime.UTC),
    )

    await ArticleFlow.summary_prune(article=article)

    assert article.summary == (
        "Считается одним из лучших нападающих в мире. "
        "Кавалер Командорского креста ордена Возрождения Польши. "
        "«Бе́шеные псы» (англ. Reservoir Dogs) — дебютный фильм. "
        "в составе сборника на платформе iOS. итальянский 3D-анимированный "
        "Rainbow CGI совместно с Rai Fictionruen, "
        "Евге́ний Петро́вич Петро́в (настоящая фамилия — Катаев; 30 ноября "
        "[13 декабря] 1902, Одесса"
    )


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 9:00:01", tick=True)
async def test_good_article_send1(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    sender = MockSender()
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)

    res = await af.send_article_good(last_article_good=None)

    assert res is False


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 10:00:01", tick=True)
async def test_good_article_send2(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    sender = MockSender()
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)

    res = await af.send_article_good(last_article_good=None)

    assert res is True


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 9:00:01", tick=True)
async def test_good_article_send3(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    sender = MockSender()
    article1 = ArticleGood(
        region="ru",
        summary="test",
        link="https://example.com",
        image_link="https://example.com",
        send_time=datetime.datetime.now(datetime.UTC).replace(day=22, hour=23, minute=0, second=0, microsecond=0),
    )
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)

    res = await af.send_article_good(last_article_good=article1)

    assert res is False


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 10:00:01", tick=True)
async def test_good_article_send4(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    sender = MockSender()
    article1 = ArticleGood(
        region="ru",
        summary="test",
        link="https://example.com",
        image_link="https://example.com",
        send_time=datetime.datetime.now(datetime.UTC).replace(day=22, hour=23, minute=0, second=0, microsecond=0),
    )
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)

    res = await af.send_article_good(last_article_good=article1)

    assert res is True


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 11:00:01", tick=True)
async def test_good_article_send5(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    sender = MockSender()
    article1 = ArticleGood(
        region="ru",
        summary="test",
        link="https://example.com",
        image_link="https://example.com",
        send_time=datetime.datetime.now(datetime.UTC).replace(hour=10, minute=2, second=0, microsecond=0),
    )
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)

    res = await af.send_article_good(last_article_good=article1)

    assert res is False


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-04-23 12:00:01", tick=True)
async def test_good_article_send6(
    session_factory: tp.Callable[[], tp.Any],
    first_region: RegionPublic,
    remove_old_data: None,
) -> None:
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    sender = MockSender()
    article1 = ArticleGood(
        region="ru",
        summary="test",
        link="https://example.com",
        image_link="https://example.com",
        send_time=datetime.datetime.now(datetime.UTC).replace(hour=10, minute=2, second=0, microsecond=0),
    )
    af = ArticleFlow(region=first_region, uow=uow, scraper=Scraper, sender=sender)

    res = await af.send_article_good(last_article_good=article1)

    assert res is True
