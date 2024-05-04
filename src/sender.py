import asyncio
import typing as tp

import aiogram

from src.models import Article
from src.pipeline import AbstractSender


class TgSender(AbstractSender):
    def __init__(self) -> None:
        # @wiki_channel_admin_bot
        token = "7026105603:AAEbEufOUPYxR2A34hfLV1PDVO24bPb3Huc"
        self.bot = aiogram.Bot(token=token)
        self.dp = aiogram.Dispatcher()
        self.router = aiogram.Router()

    async def send_article(self, article: Article, region_channel: str) -> None:
        if not article.image_link:
            await self.bot.send_message(
                chat_id=region_channel,
                text=article.summary,
                parse_mode="HTML",
            )
        else:
            await self.bot.send_photo(
                chat_id=region_channel, caption=article.summary, photo=article.image_link, parse_mode="HTML"
            )

    # async def start_polling(self) -> None:
    #     # await self.bot.send_message(
    #     #     chat_id="@wikipedia_daily_ru",
    #     #     text="hi",
    #     # )
    #     try:
    #         await self.dp.start_polling(self.bot, handle_signals=False)
    #     except asyncio.CancelledError:
    #         pass
    #
    # async def stop_polling(self) -> None:
    #     try:
    #         await self.dp.stop_polling()
    #     except RuntimeError:
    #         pass
    #
    # @staticmethod
    # async def incoming_message_transform(message: aiogram.types.Message) -> tuple[str, str, int]:
    #     try:
    #         text = str(message.text)
    #         user_id = str(message.from_user.id)
    #     except Exception as e:
    #         raise e
    #     return text, user_id, message.chat.id
    #
    # async def register_text_message_handler(self, func: tp.Callable[[tp.Any], tp.Awaitable[None]]) -> None:
    #     self.router.message.register(func)
    #     self.dp.include_router(self.router)
