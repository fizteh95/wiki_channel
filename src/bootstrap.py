import typing as tp

import settings

from src.orm import create_engine, start_mappers
from src.pipeline import ArticleFlow
from src.repo import Repository
from src.scraper import Scraper
from src.sender import TgSender
from src.uow import UnitOfWork


async def bootstrap() -> tp.Any:
    start_mappers()
    session_factory = create_engine(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        name=settings.DB_NAME,
    )
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    async with uow.atomic() as repo:
        regions = await repo.get_regions()

    sender = TgSender()
    article_flow = ArticleFlow(uow=uow, sender=sender, scraper=Scraper, region=regions[0])
    return [article_flow.article_day_loop, article_flow.article_good_loop]


async def bootstrap_for_probe() -> tp.Any:
    start_mappers()
    session_factory = create_engine(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        name=settings.DB_NAME,
    )
    uow = UnitOfWork(db_collaborator=Repository, db_session_factory=session_factory)
    async with uow.atomic() as repo:
        regions = await repo.get_regions()

    sender = TgSender()
    article_flow = ArticleFlow(uow=uow, sender=sender, scraper=Scraper, region=regions[0])
    return article_flow._probe_send()  # noqa
