import pytest

from src.scraper import Scraper


@pytest.mark.asyncio
async def test_getting_article_day() -> None:
    s = Scraper()
    await s.get_article_of_day(region=None)
    raise
