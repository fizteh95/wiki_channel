import pytest

from src.models import RegionPublic
from src.scraper import Scraper


@pytest.mark.asyncio
async def test_parsing_main_page(first_region: RegionPublic) -> None:
    s = Scraper()
    with open("./tests/resources/main_page.html", "r", encoding="utf-8") as file:
        content = file.read()

    a = await s.parse_main_page(content=content, region=first_region)

    assert a.link == "https://ru.wikipedia.orghttps://ru.wikipedia.org/wiki/Формоз"
    assert a.image_link == "https://ru.wikipedia.orghttps://commons.wikimedia.org/wiki/File:111.Formosus.jpg?uselang=ru"
    assert len(a.summary) == 569


@pytest.mark.asyncio
async def test_parsing_article_good_table(first_region: RegionPublic) -> None:
    s = Scraper()
    with open("./tests/resources/favourite_articles.html", "r", encoding="utf-8") as file:
        content = file.read()

    a = await s.parse_good_article_table(content=content)

    assert len(a) >= 1876


@pytest.mark.asyncio
async def test_parsing_good_article(first_region: RegionPublic) -> None:
    s = Scraper()
    with open("./tests/resources/good_article.html", "r", encoding="utf-8") as file:
        content = file.read()

    a = await s.parse_good_article(content=content, region=first_region, link="123")

    assert len(a.summary) == 2767


@pytest.mark.asyncio
async def test_get_article_day(first_region: RegionPublic) -> None:
    ...
