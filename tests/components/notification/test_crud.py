# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import pytest

from notification.components.exceptions import NotFound


class TestNotificationCRUD:
    async def test_create_from_announcement_creates_maintenance_notification_with_same_information(
        self, announcement_factory, notification_crud
    ):
        created_announcement = await announcement_factory.create()

        received_notification = await notification_crud.create_from_announcement(created_announcement)

        assert received_notification.announcement_id == created_announcement.id
        assert received_notification.effective_date == created_announcement.effective_date
        assert received_notification.duration_minutes == created_announcement.duration_minutes
        assert received_notification.message == created_announcement.message

    async def test_delete_by_announcement_id_removes_maintenance_notifications_with_announcement_id(
        self, notification_factory, notification_crud
    ):
        created_notification = await notification_factory.create_maintenance()

        await notification_crud.delete_by_announcement_id(created_notification.announcement_id)

        with pytest.raises(NotFound):
            await notification_crud.retrieve_by_id(created_notification.id)
