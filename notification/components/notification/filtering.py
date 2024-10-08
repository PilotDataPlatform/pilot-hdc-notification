# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from datetime import datetime

from pydantic import Field
from pydantic import conset
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.sql import Select

from notification.components.filtering import Filtering
from notification.components.notification.models import Notification
from notification.components.notification.models import NotificationType


class NotificationFiltering(Filtering):
    """Notifications filtering control parameters."""

    type_: NotificationType | None = Field(None, alias='type')
    recipient_username: str | None = None
    project_code_any: conset(str, min_items=1) | None = None
    created_at_start: datetime | None = None
    created_at_end: datetime | None = None

    def apply(self, statement: Select, model: type[Notification]) -> Select:
        """Return statement with applied filtering."""

        if self.type_:
            statement = statement.where(model.type == self.type_)

        if isinstance(self.recipient_username, str):
            where_clause = model.recipient_username == self.recipient_username
            if self.recipient_username == '':
                where_clause = model.recipient_username.is_(None)
            statement = statement.where(where_clause)

        if self.project_code_any:
            statement = statement.where(model.project_code.in_(self.project_code_any))

        if self.created_at_start:
            statement = statement.where(model.created_at >= self.created_at_start)

        if self.created_at_end:
            statement = statement.where(model.created_at <= self.created_at_end)

        return statement


class UserNotificationFiltering(Filtering):
    """Notifications filtering control parameters.

    Includes all notifications user is allowed to access.
    """

    recipient_username: str
    project_code_any: conset(str, min_items=0)

    def apply(self, statement: Select, model: type[Notification]) -> Select:
        """Return statement with applied filtering."""

        recipient_bind_types = {NotificationType.PIPELINE, NotificationType.COPY_REQUEST, NotificationType.ROLE_CHANGE}

        statement = statement.where(
            or_(
                and_(model.type.in_(recipient_bind_types), model.recipient_username == self.recipient_username),
                and_(
                    model.type == NotificationType.PROJECT,
                    or_(not self.project_code_any, model.project_code.in_(self.project_code_any)),
                ),
                and_(model.type == NotificationType.MAINTENANCE),
            )
        )

        return statement
