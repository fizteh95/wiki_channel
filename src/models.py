import datetime
from dataclasses import dataclass


@dataclass
class RegionPublic:
    country_code: str
    country: str
    channel_id: str
    utc_hour_to_send_day: int
    utc_minute_to_send_day: int
    intervals_for_good_article: str
    main_page_suffix: str
    favourite_page_suffix: str


@dataclass
class Article:
    region: str  # region: RegionPublic
    link: str
    image_link: str | None
    summary: str
    send_time: datetime.datetime | None = None
    title: str | None = None


@dataclass
class ArticleDay(Article):
    """
    Статья дня
    """


@dataclass
class ArticleGood(Article):
    """
    Хорошая статья
    """


@dataclass
class ArticleGoodPreparsed:
    """
    Заготовка для хороших статей
    """

    link: str
    title: str
