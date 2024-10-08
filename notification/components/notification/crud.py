# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from uuid import UUID

from sqlalchemy import delete

from notification.components.announcement.models import Announcement
from notification.components.crud import CRUD
from notification.components.notification.models import MaintenanceNotification
from notification.components.notification.models import Notification
from notification.components.notification.schemas import MaintenanceNotificationCreateSchema


class NotificationCRUD(CRUD):
    """CRUD for managing notification database models."""

    model = Notification

    async def create_from_announcement(self, announcement: Announcement) -> MaintenanceNotification:
        """Create maintenance notification from announcement."""

        return await self.create(
            MaintenanceNotificationCreateSchema(
                announcement_id=announcement.id,
                effective_date=announcement.effective_date,
                duration_minutes=announcement.duration_minutes,
                message=announcement.message,
            )
        )

    async def retrieve_by_announcement_id(self, announcement_id: UUID) -> MaintenanceNotification:
        """Get existing maintenance notification by announcement id."""

        statement = self.select_query.where(self.model.data.contains({'announcement_id': str(announcement_id)}))

        return await self._retrieve_one(statement)

    async def delete_by_announcement_id(self, announcement_id: UUID) -> None:
        """Remove existing maintenance notification by announcement id."""

        statement = (
            delete(self.model)
            .where(self.model.data.contains({'announcement_id': str(announcement_id)}))
            .execution_options(synchronize_session='fetch')
        )

        await self._delete(statement)
