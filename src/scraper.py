import random
from urllib import parse

import aiohttp
import bs4.element

# import wikipedia
from bs4 import BeautifulSoup

from src.models import ArticleDay, ArticleGood, ArticleGoodPreparsed, RegionPublic
from src.pipeline import ArticleScraper


class Scraper(ArticleScraper):
    async def get_fullsize_image(self, page_link: str) -> str:
        """
        Получение ссылки на полноразмерную картинку
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url=page_link) as resp:
                content: str = await resp.text()

        soup = BeautifulSoup(content, "html.parser")
        quoted_image_link = soup.select_one(selector="#file > a > img")
        try:
            link = parse.unquote(quoted_image_link.get("src")[2:])
        except Exception as e:
            print(f"{e}, page_link: {page_link}")
            link = ""

        return link

    async def download_main_page(self, region: RegionPublic) -> str:
        url = f"https://{region.country_code}.wikipedia.org/wiki/{region.main_page_suffix}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                content: str = await resp.text()
        return content

    async def parse_main_page(self, content: str, region: RegionPublic) -> ArticleDay:
        soup = BeautifulSoup(content, "html.parser")
        article_of_day = soup.find("div", class_="fake-heading h2 main-header")
        encoded_link = article_of_day.find("a").get("href")
        link = parse.unquote(encoded_link)

        image_link = soup.select_one(selector="#main-tfa > div.main-box-content > figure > a")
        unquoted_image_link = parse.unquote(image_link.get("href"))

        text_container = soup.find("div", class_="main-block main-box main-box-responsive-image")
        all_text = text_container.find("div", "main-box-content")
        article_text = all_text.find("p").text

        image_link = await self.get_fullsize_image(
            page_link=f"https://{region.country_code}.wikipedia.org" + unquoted_image_link
        )

        article = ArticleDay(
            region=region.country_code,
            link=f"https://{region.country_code}.wikipedia.org" + link,
            image_link=image_link,
            summary=article_text,
        )
        return article

    async def get_article_of_day(self, region: RegionPublic) -> ArticleDay:
        content = await self.download_main_page(region=region)
        article = await self.parse_main_page(content=content, region=region)
        return article

    async def download_good_article_table(self, region: RegionPublic) -> str:
        url = f"https://{region.country_code}.wikipedia.org/wiki/{region.favourite_page_suffix}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                content: str = await resp.text()
        return content

    async def parse_good_article_table(self, content: str, region: RegionPublic) -> list[ArticleGoodPreparsed]:
        soup = BeautifulSoup(content, "html.parser")
        articles_table = soup.select_one(
            selector="#mw-content-text > div.mw-content-ltr.mw-parser-output > table > tbody > tr > td > table:nth-child(13) > tbody > tr"
        )
        articles = articles_table.findAll("a")
        result: list[ArticleGoodPreparsed] = []
        for a in articles:
            if not a.get("href").startswith("https://commons.wikimedia.org/wiki/File"):
                preparsed_article = ArticleGoodPreparsed(
                    link=f"https://{region.country_code}.wikipedia.org" + parse.unquote(a.get("href")),
                    title=a.get("title"),
                )
                result.append(preparsed_article)
        return result

    async def download_good_article(self, article: ArticleGoodPreparsed) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=article.link) as resp:
                content: str = await resp.text()
        return content

    async def parse_good_article(self, content: str, region: RegionPublic, link: str) -> ArticleGood:
        res_text = ""
        soup = BeautifulSoup(content, "html.parser")
        head_content = soup.select_one(selector="#mw-content-text > div.mw-content-ltr.mw-parser-output")
        start = False
        stop = False
        head_childran = head_content.childGenerator()
        for child in head_childran:
            if not start and not stop and child.name == "p":
                start = True
            if start and not stop and child.name != "p":
                stop = True
            if (start or stop) and not (start and stop):
                res_text += child.text

        images = soup.findAll("img")
        unquoted_image_link = ""
        for i in images:
            if i.get("alt") in ["Эта статья входит в число статей года", "Эта статья входит в число избранных"]:
                continue
            image_parent = i.parent
            image_link = image_parent.get("href")
            unquoted_image_link = parse.unquote(image_link)
            image_link = await self.get_fullsize_image(
                page_link=f"https://{region.country_code}.wikipedia.org" + unquoted_image_link
            )
            break

        article = ArticleGood(
            region=region.country_code,  # typing: ignore  # noqa
            link=link,
            image_link=image_link,
            summary=res_text,
        )
        return article

    async def get_random_good_article(self, region: RegionPublic) -> ArticleGood:
        content = await self.download_good_article_table(region=region)
        article_list = await self.parse_good_article_table(content=content, region=region)
        unparsed_article = random.choice(article_list)
        article_content = await self.download_good_article(article=unparsed_article)
        article = await self.parse_good_article(content=article_content, region=region, link=unparsed_article.link)
        return article
