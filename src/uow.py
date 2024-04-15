import typing as tp
from contextlib import asynccontextmanager


class DBCollaborator:
    def __init__(self, session: tp.Any):
        self.session = session


class UnitOfWork:
    def __init__(
        self,
        db_collaborator: type[DBCollaborator],
        db_session_factory: tp.Callable[[], tp.Any],
    ) -> None:
        self.db_collaborator = db_collaborator  # ТИП!!!!!
        self.db_session_factory = db_session_factory  # ФУНКЦИЯ!!!!!

    @asynccontextmanager
    async def atomic(self) -> tp.AsyncIterator[tp.Any]:
        session = self.db_session_factory()
        repo = self.db_collaborator(session=session)
        try:
            yield repo
        except Exception as e:
            print(e)
            await repo.session.rollback()
            raise e
        else:
            await repo.session.commit()
        finally:
            await repo.session.aclose()
