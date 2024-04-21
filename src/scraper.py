from urllib import parse

import aiohttp
# import wikipedia
from bs4 import BeautifulSoup

from src.models import ArticleDay, ArticleGood, RegionPublic
from src.pipeline import ArticleScraper


class Scraper(ArticleScraper):
    async def get_article_of_day(self, region: RegionPublic) -> ArticleDay:
        url = f"https://{region.country_code}.wikipedia.org/wiki/{region.main_page_suffix}"
        # "https://ru.wikipedia.org/wiki/Заглавная_страница"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                content = await resp.text()

        soup = BeautifulSoup(content, "html.parser")
        article_of_day = soup.find("div", class_="fake-heading h2 main-header")
        encoded_link = article_of_day.find("a").get("href")
        link = parse.unquote(encoded_link)

        image_link = soup.select_one(selector="#main-tfa > div.main-box-content > figure > a")
        unquoted_image_link = parse.unquote(image_link.get("href"))

        text_container = soup.find("div", class_="main-block main-box main-box-responsive-image")
        all_text = text_container.find("div", "main-box-content")
        article_text = all_text.find("p").text

        # TODO: get image true link

        article = ArticleDay(
            region=region.id,  # typing: ignore  # noqa
            link=f"https://{region.country_code}.wikipedia.org" + link,
            image_link=f"https://{region.country_code}.wikipedia.org" + unquoted_image_link,
            summary=article_text,
        )
        return article

    async def get_random_good_article(self, region: RegionPublic) -> ArticleGood:
        raise NotImplementedError
