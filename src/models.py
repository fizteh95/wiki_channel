import datetime
from dataclasses import dataclass


@dataclass
class RegionPublic:
    country_code: str
    country: str
    channel_id: str
    utc_hour_to_send_day: int
    utc_minute_to_send_day: int
    interval_for_goof_article: int


@dataclass
class Article:
    region: int  # region: RegionPublic
    link: str
    image_link: str
    summary: str
    send_time: datetime.datetime


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
