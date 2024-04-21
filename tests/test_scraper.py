import pytest

from src.models import RegionPublic
from src.scraper import Scraper


@pytest.mark.asyncio
async def test_getting_article_day(first_region: RegionPublic) -> None:
    s = Scraper()
    a = await s.get_article_of_day(region=first_region)
    print(a)
    raise


@pytest.mark.asyncio
async def test_getting_article_good() -> None:
    s = Scraper()
    await s.get_article_of_day(region=None)
    raise
