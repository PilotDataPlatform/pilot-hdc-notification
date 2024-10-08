# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from sqlalchemy.future import select
from sqlalchemy.sql import Select

from notification.components.announcement import Announcement
from notification.components.announcement import AnnouncementUnsubscription
from notification.components.filtering import Filtering


class AnnouncementFiltering(Filtering):
    """Announcements filtering control parameters."""

    username: str | None = None

    def apply(self, statement: Select, model: type[Announcement]) -> Select:
        """Return statement with applied filtering."""

        if self.username:
            unsubscribed_announcement_ids = select(AnnouncementUnsubscription.announcement_id).where(
                AnnouncementUnsubscription.username == self.username
            )
            statement = statement.where(model.id.not_in(unsubscribed_announcement_ids))

        return statement
