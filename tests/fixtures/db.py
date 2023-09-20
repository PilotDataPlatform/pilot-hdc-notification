# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

import os
from contextlib import contextmanager
from pathlib import Path

import pytest
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer


@contextmanager
def chdir(directory: Path) -> None:
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture(scope='session')
def db_uri(get_service_image, project_root) -> str:
    postgres_image = get_service_image('postgres')

    with PostgresContainer(postgres_image) as postgres:
        postgres_uri = postgres.get_connection_url()

        config = Config('migrations/alembic.ini')
        with chdir(project_root):
            config.set_main_option('database_uri', postgres_uri)
            upgrade(config, 'head')

        yield postgres_uri.replace('+psycopg2', '+asyncpg')


@pytest.fixture
async def db_session(db_uri) -> AsyncSession:
    db_engine = create_async_engine(db_uri)
    autocommit_engine = db_engine.execution_options(isolation_level='AUTOCOMMIT')
    session = AsyncSession(bind=autocommit_engine, expire_on_commit=False)

    try:
        yield session
    finally:
        await session.close()
