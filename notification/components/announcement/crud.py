# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy.future import select

from notification.components.announcement.models import Announcement
from notification.components.announcement.models import AnnouncementUnsubscription
from notification.components.crud import CRUD


class AnnouncementCRUD(CRUD):
    """CRUD for managing announcement database models."""

    model = Announcement

    async def unsubscribe_user(self, announcement_id: UUID, username: str) -> None:
        """Create announcement unsubscription for the announcement id and username."""

        statement = insert(AnnouncementUnsubscription).values(announcement_id=announcement_id, username=username)

        await self._create_one(statement)

    async def subscribe_all_users(self, announcement_id: UUID) -> None:
        """Remove existing announcement unsubscriptions for the announcement id."""

        statement = delete(AnnouncementUnsubscription).where(
            AnnouncementUnsubscription.announcement_id == announcement_id
        )

        await self._delete(statement)

    async def list_unsubscriptions(self, announcement_id: UUID) -> list[AnnouncementUnsubscription]:
        """Get existing announcement unsubscriptions for the announcement id."""

        statement = select(AnnouncementUnsubscription).where(
            AnnouncementUnsubscription.announcement_id == announcement_id
        )

        return await self._retrieve_many(statement)
