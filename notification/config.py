# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import logging
from functools import lru_cache
from typing import Any

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra


class VaultConfig(BaseSettings):
    """Store vault related configuration."""

    APP_NAME: str = 'notification'
    CONFIG_CENTER_ENABLED: bool = False

    VAULT_URL: str | None
    VAULT_CRT: str | None
    VAULT_TOKEN: str | None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def load_vault_settings(settings: BaseSettings) -> dict[str, Any]:
    config = VaultConfig()

    if not config.CONFIG_CENTER_ENABLED:
        return {}

    client = VaultClient(config.VAULT_URL, config.VAULT_CRT, config.VAULT_TOKEN)
    return client.get_from_vault(config.APP_NAME)


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'notification'
    HOST: str = '127.0.0.1'
    PORT: int = 5065
    WORKERS: int = 1
    RELOAD: bool = False

    LOGGING_LEVEL: int = logging.INFO
    LOGGING_FORMAT: str = 'json'

    POSTFIX: str = ''
    SMTP_USER: str = 'user'
    SMTP_PASS: str = 'pass'
    SMTP_PORT: int = 0
    POSTFIX_URL: str = 'mailhog'
    POSTFIX_PORT: int = 1025
    ALLOWED_EXTENSIONS: set[str] = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    IMAGE_EXTENSIONS: set[str] = {'png', 'jpg', 'jpeg', 'gif'}
    EMAIL_ATTACHMENT_MAX_SIZE_BYTES: int = 2 * 1024**2  # 2 MB
    RDS_HOST: str = 'db'
    RDS_PORT: str = '5432'
    RDS_USER: str = 'postgres'
    RDS_PWD: str = 'passwordRoJi'
    RDS_DB_NAME: str = 'notification'
    RDS_ECHO_SQL_QUERIES: bool = False

    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

        self.RDS_DB_URI = (
            f'postgresql+asyncpg://{self.RDS_USER}:{self.RDS_PWD}@{self.RDS_HOST}:{self.RDS_PORT}/{self.RDS_DB_NAME}'
        )

        if self.POSTFIX != '' and self.SMTP_PORT:
            self.POSTFIX_URL = self.POSTFIX
            self.POSTFIX_PORT = self.SMTP_PORT

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return init_settings, env_settings, load_vault_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = get_settings()
