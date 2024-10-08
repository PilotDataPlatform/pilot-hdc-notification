# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from __future__ import annotations as _annotations

import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi import FastAPI
from httpx import AsyncClient

from notification.app import create_app
from notification.config import Settings
from notification.config import get_settings


class OverrideDependencies(AbstractContextManager):
    """Temporarily override application dependencies using context manager."""

    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.stashed_dependencies = {}
        self.dependencies_to_override = {}

    def __call__(self, dependencies: dict[Callable[..., Any], Callable[..., Any]]) -> OverrideDependencies:
        self.dependencies_to_override = dependencies
        return self

    def __enter__(self) -> OverrideDependencies:
        self.stashed_dependencies = self.app.dependency_overrides.copy()
        self.app.dependency_overrides.update(self.dependencies_to_override)
        return self

    def __exit__(self, *args: Any) -> None:
        self.app.dependency_overrides.clear()
        self.app.dependency_overrides.update(self.stashed_dependencies)
        self.dependencies_to_override = {}
        return None


@pytest.fixture
def override_dependencies(app) -> OverrideDependencies:
    yield OverrideDependencies(app)


@pytest.fixture(scope='session')
def project_root() -> Path:
    path = Path(__file__)

    while path.name != 'notification':
        path = path.parent

    yield path


@pytest.fixture(scope='session')
def get_service_image(project_root) -> Callable[[str], str]:
    with open(project_root / 'docker-compose.yaml') as file:
        services = yaml.safe_load(file)['services']

    def get_image(service_name: str) -> str:
        return services[service_name]['image']

    yield get_image


@pytest.fixture(scope='session')
def event_loop() -> AbstractEventLoop:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    yield loop
    loop.close()


@pytest.fixture(scope='session')
def settings(db_uri) -> Settings:
    settings = get_settings()
    settings.RDS_DB_URI = db_uri
    yield settings


@pytest.fixture
def app(event_loop, settings) -> FastAPI:
    app = create_app()
    yield app


@pytest.fixture
async def client(app) -> AsyncClient:
    async with AsyncClient(app=app, base_url='https://notification') as client:
        yield client
