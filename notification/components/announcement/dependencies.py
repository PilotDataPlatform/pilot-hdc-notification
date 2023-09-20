# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from notification.components.announcement.crud import AnnouncementCRUD
from notification.dependencies import get_db_session


def get_announcement_crud(db_session: AsyncSession = Depends(get_db_session)) -> AnnouncementCRUD:
    """Return an instance of AnnouncementCRUD as a dependency."""

    return AnnouncementCRUD(db_session)
