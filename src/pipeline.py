import asyncio
import datetime
import typing as tp
from abc import ABC, abstractmethod

from src.models import Article, ArticleDay, ArticleGood, RegionPublic
from src.uow import UnitOfWork


class AbstractRepo(ABC):
    @abstractmethod
    async def create_region(self, region: RegionPublic) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_regions(self) -> list[RegionPublic]:
        raise NotImplementedError

    @abstractmethod
    async def create_article_of_day(self, article: ArticleDay) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_good_article(self, article: ArticleGood) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_last_article_of_day(self, region_code: str) -> ArticleDay | None:
        raise NotImplementedError

    @abstractmethod
    async def get_last_good_article(self, region_code: str) -> ArticleGood | None:
        raise NotImplementedError


class AbstractSender(ABC):
    @abstractmethod
    async def send_article(self, article: Article, region_channel: str) -> None:
        raise NotImplementedError


class ArticleScraper(ABC):
    @abstractmethod
    async def get_article_of_day(self, region: RegionPublic) -> ArticleDay:
        raise NotImplementedError

    @abstractmethod
    async def get_random_good_article(self, region: RegionPublic) -> ArticleGood:
        raise NotImplementedError


class ArticleFlow:
    def __init__(
        self, region: RegionPublic, uow: UnitOfWork, sender: AbstractSender, scraper: type[ArticleScraper]
    ) -> None:
        self.region = region
        self.uow = uow
        self.sender = sender
        self.scraper = scraper
        self.ad_loop = True
        self.ag_loop = True

    @staticmethod
    async def summary_prune(article: Article) -> None:
        print(article.summary[:2000])
        if len(article.summary) <= 1024:
            return
        counter = 0
        print(len(article.summary))
        # TODO: make prune normal
        # TODO: remove [1] - references
        while len(article.summary) > 1024 and counter < 30:
            counter += 1
            print(len(article.summary))
            index_of_last_dot = article.summary[:-1].rfind(".")
            article.summary = article.summary[:index_of_last_dot + 1]
        return

    async def send_article_day(self, last_article_day: ArticleDay | None, new_article: ArticleDay) -> bool:
        """
        Берем время когда надо отправлять статью дня
        Берем последнее отправленное сообщение по региону
        Получаем ссылку на статью дня региона
        Если (текущее время больше времени отправки региона) и (ссылка не равна ссылке из последнего сообщения)
        то в транзакции отправляем сообщение в канал и сохраняем его в базу
        :return:
        """
        now = datetime.datetime.now(datetime.UTC)
        if last_article_day is None:
            return True
        if (
            now.hour > self.region.utc_hour_to_send_day
            or (now.hour == self.region.utc_hour_to_send_day and now.minute > self.region.utc_minute_to_send_day)
        ) and (last_article_day.link != new_article.link):
            return True
        return False

    async def send_article_good(self, last_article_good: ArticleGood | None) -> bool:
        if last_article_good is None:
            return True
        now = datetime.datetime.now(datetime.UTC)
        if (now - last_article_good.send_time).seconds // 60 >= self.region.interval_for_goof_article:
            return True
        return False

    async def article_day_scheduled(self) -> None:
        scraper = self.scraper()
        new_article_day = await scraper.get_article_of_day(region=self.region)
        print("tp1")
        async with self.uow.atomic() as repo:
            last_article_day = await repo.get_last_article_of_day(region_code=self.region.country_code)
            print("tp2")
            to_send = await self.send_article_day(last_article_day=last_article_day, new_article=new_article_day)
            print("tp3")
            print(to_send)
            if not to_send:
                return
            await self.summary_prune(article=new_article_day)
            await repo.create_article_of_day(article=new_article_day)
            await self.sender.send_article(article=new_article_day, region_channel=self.region.channel_id)

    async def article_good_scheduled(self) -> None:
        scraper = self.scraper()
        new_article_good = await scraper.get_random_good_article(region=self.region)
        print("scraped")
        async with self.uow.atomic() as repo:
            last_article_good = await repo.get_last_good_article(region_code=self.region.country_code)
            to_send = await self.send_article_good(last_article_good=last_article_good)
            print(f"to send good: {to_send}")
            if not to_send:
                return
            await self.summary_prune(article=new_article_good)
            print("pruned")
            await repo.create_good_article(article=new_article_good)
            await self.sender.send_article(article=new_article_good, region_channel=self.region.channel_id)

    async def article_day_loop(self) -> None:
        while self.ad_loop:
            try:
                await self.article_day_scheduled()
                await asyncio.sleep(53)
            except Exception as e:
                print(f"ad loop exception: {e}")
                await asyncio.sleep(180)

    async def article_good_loop(self) -> None:
        while self.ag_loop:
            try:
                await self.article_good_scheduled()
                await asyncio.sleep(53)
            except Exception as e:
                print(f"ad loop exception: {e}")
                await asyncio.sleep(180)
