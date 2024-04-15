import typer
from alembic import command
from alembic.config import Config

app = typer.Typer()


@app.command()
def run() -> None:
    """
    Start service
    """
    print("Im running!")


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
