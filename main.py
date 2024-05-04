import asyncio
import typing as tp

import typer
from alembic import command
from alembic.config import Config

from src.bootstrap import bootstrap, bootstrap_for_probe
from src.sender import TgSender

app = typer.Typer()


async def start_service() -> tp.Any:
    day_loop, good_loop = await bootstrap()
    await asyncio.gather(day_loop(), good_loop())


async def probe_send() -> None:
    probe_func = await bootstrap_for_probe()
    await asyncio.gather(probe_func())


@app.command()
def run() -> None:
    """
    Start service
    """
    print("Im running!")
    asyncio.run(start_service())


@app.command()
def probe() -> None:
    """
    Probe article parse and send
    """
    print("Probing...")
    asyncio.run(probe_send())
    print("Probe done!")


# async def print_info(message: tp.Any) -> None:
#     text, user_id, message_chat_id = await TgSender.incoming_message_transform(message=message)
#     print(f"{text} from {user_id} in {message_chat_id}")
#
#
# async def start_debug() -> None:
#     sender = TgSender()
#     await sender.register_text_message_handler(func=print_info)
#     await sender.start_polling()
#     await sender.stop_polling()
#
#
# @app.command()
# def find_channel() -> None:
#     """
#     Find tg channel chat_id
#     """
#     asyncio.run(start_debug())


@app.command()
def create_migrations() -> None:
    """
    Create migration files for new code
    """
    alembic_cfg = Config("./alembic.ini")
    command.revision(alembic_cfg, autogenerate=True)


@app.command()
def migrate() -> None:
    """
    Apply migration in database
    """
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    app()
