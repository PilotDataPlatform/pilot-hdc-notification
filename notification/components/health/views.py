# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import Response

from notification.components.health.db_checker import DBChecker
from notification.components.health.dependencies import get_db_checker
from notification.logger import logger

router = APIRouter(prefix='/health', tags=['Health'])


@router.get('/', summary='Healthcheck if database is online.')
async def get_db_status(db_checker: DBChecker = Depends(get_db_checker)) -> Response:
    """Return response that represents status of the database."""

    logger.info('Checking if database is online.')

    is_online = await db_checker.is_online()

    logger.info(f'Received is_online status "{is_online}".')

    response = Response(status_code=204)
    if not is_online:
        response = Response(status_code=503)

    return response
