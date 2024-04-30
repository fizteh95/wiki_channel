import datetime  # noqa
from typing import cast

from sqlalchemy import delete, select
from sqlalchemy.sql.expression import ColumnElement  # noqa

from src.models import ArticleDay, ArticleGood, RegionPublic
from src.pipeline import AbstractRepo
from src.uow import DBCollaborator


class Repository(DBCollaborator, AbstractRepo):
    async def create_region(self, region: RegionPublic) -> None:
        self.session.add(region)

    async def get_regions(self) -> list[RegionPublic]:
        result = await self.session.scalars(select(RegionPublic))
        regions: list[RegionPublic] = result.all()
        return regions

    async def create_article_of_day(self, article: ArticleDay) -> None:
        article.send_time = datetime.datetime.now(datetime.UTC)
        self.session.add(article)

    async def create_good_article(self, article: ArticleGood) -> None:
        article.send_time = datetime.datetime.now(datetime.UTC)
        self.session.add(article)

    async def get_last_article_of_day(self, region_code: str) -> ArticleDay | None:
        regions = await self.session.scalars(
            select(RegionPublic).where(cast("ColumnElement[bool]", RegionPublic.country_code == region_code))
        )
        region = regions.first()
        if region is None:
            raise Exception(f"Region with region code {region_code} not found!")
        articles = await self.session.scalars(
            select(ArticleDay)
            .where(cast("ColumnElement[bool]", ArticleDay.region == region.country_code))
            .order_by(cast("ColumnElement[datetime.datetime]", ArticleDay.send_time.desc()))  # type: ignore
        )
        article: ArticleDay | None = articles.first()
        return article

    async def get_last_good_article(self, region_code: str) -> ArticleGood | None:
        regions = await self.session.scalars(
            select(RegionPublic).where(cast("ColumnElement[bool]", RegionPublic.country_code == region_code))
        )
        region = regions.first()
        if region is None:
            raise Exception(f"Region with region code {region_code} not found!")
        articles = await self.session.scalars(
            select(ArticleGood)
            .where(cast("ColumnElement[bool]", ArticleGood.region == region.country_code))
            .order_by(cast("ColumnElement[datetime.datetime]", ArticleGood.send_time.desc()))  # type: ignore
        )
        article: ArticleGood | None = articles.first()
        return article

    async def remove_all(self) -> None:
        await self.session.execute(delete(RegionPublic).where(RegionPublic.id > 0))  # type: ignore
        await self.session.execute(delete(ArticleDay).where(ArticleDay.id > 0))  # type: ignore
        await self.session.execute(delete(ArticleGood).where(ArticleGood.id > 0))  # type: ignore
