# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from unittest.mock import AsyncMock
from unittest.mock import Mock

from sqlalchemy.exc import SQLAlchemyError

from notification.components.health.db_checker import DBChecker
from notification.components.health.dependencies import get_db_checker


class TestHealthViews:
    async def test_health_endpoint_returns_204_when_db_is_live(self, client):
        response = await client.get('/v1/health/')

        assert response.status_code == 204

    async def test_health_endpoint_returns_503_when_db_is_not_live(self, client, override_dependencies):
        def db_checker():
            session = Mock()
            session.execute = AsyncMock(side_effect=SQLAlchemyError)
            return DBChecker(session)

        with override_dependencies({get_db_checker: db_checker}):
            response = await client.get('/v1/health/')

        assert response.status_code == 503
        assert response.text == ''
