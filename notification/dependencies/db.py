# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from notification.config import Settings
from notification.config import get_settings


class GetDBEngine:
    """Create a FastAPI callable dependency for SQLAlchemy single AsyncEngine instance."""

    def __init__(self) -> None:
        self.instance = None

    async def __call__(self, settings: Settings = Depends(get_settings)) -> AsyncEngine:
        """Return an instance of AsyncEngine class."""

        if not self.instance:
            self.instance = create_async_engine(settings.RDS_DB_URI, echo=settings.RDS_ECHO_SQL_QUERIES)
        return self.instance


get_db_engine = GetDBEngine()


async def get_db_session(engine=Depends(get_db_engine)) -> AsyncSession:
    """Create a FastAPI callable dependency for SQLAlchemy AsyncSession instance."""

    db = AsyncSession(bind=engine, expire_on_commit=False)
    try:
        yield db
    finally:
        await db.close()
