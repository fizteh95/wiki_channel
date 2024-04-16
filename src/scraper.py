from urllib import parse

import aiohttp
import wikipedia
from bs4 import BeautifulSoup

from src.models import ArticleDay, ArticleGood, RegionPublic
from src.pipeline import ArticleScraper


class Scraper(ArticleScraper):
    async def get_article_of_day(self, region: RegionPublic) -> ArticleDay:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://ru.wikipedia.org/wiki/Заглавная_страница") as resp:
                print(resp.status)
                # print(await resp.text())

                content = await resp.text()

        soup = BeautifulSoup(content, "html.parser")
        article_of_day = soup.find("div", class_="fake-heading h2 main-header")
        encoded_link = article_of_day.find("a").get("href")
        link = parse.unquote(encoded_link)
        print(link)

        text_container = soup.find("div", class_="main-block main-box main-box-responsive-image")
        print(text_container.find("div", "main-box-content").text)

        # good_card_tag = "div.catalog-item.ddl_product.catalog-item-desktop"
        # item_title_tag = "div.item-title"
        #
        # items = soup.select(good_card_tag)
        #
        # item_title_el = soup.select(item_title_tag)[0]
        #
        # item_title_text = item_title_el.text
        # item_title_text = item_title_text.replace("\n", "")
        # item_title_text = item_title_text.replace("\t", "")
        #
        # item_href = item_title_el.select("a")[0]
        # item_href_text = item_href["href"]

    async def get_random_good_article(self, region: RegionPublic) -> ArticleGood:
        raise NotImplementedError
