# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from logging.config import fileConfig
from urllib.parse import urlparse

from alembic import context
from common import LoggerFactory
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from notification.components.db_model import DBModel
from notification.config import get_settings

config = context.config
fileConfig(config.config_file_name)
settings = get_settings()

logger = LoggerFactory(
    'alembic',
    level_default=settings.LOG_LEVEL_DEFAULT,
    level_file=settings.LOG_LEVEL_FILE,
    level_stdout=settings.LOG_LEVEL_STDOUT,
    level_stderr=settings.LOG_LEVEL_STDERR,
).get_logger()
target_metadata = DBModel.metadata
database_uri = config.get_main_option('database_uri', settings.RDS_DB_URI)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    url = database_uri.replace(f'{urlparse(database_uri).scheme}://', 'postgresql://', 1)
    connectable = create_engine(url, poolclass=NullPool, echo=settings.RDS_ECHO_SQL_QUERIES)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    logger.error('Offline migrations environment is not supported.')
    exit(1)

run_migrations_online()
