# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from datetime import datetime

from fastapi import Query
from pydantic import validator

from notification.components.notification.filtering import NotificationFiltering
from notification.components.notification.filtering import UserNotificationFiltering
from notification.components.notification.models import NotificationType
from notification.components.parameters import FilterParameters
from notification.components.parameters import SortByFields


class NotificationSortByFields(SortByFields):
    """Fields by which notifications can be sorted."""

    CREATED_AT = 'created_at'


def split_list_parameters(value: str) -> list[str]:
    """Split string with comma-separated values into list of strings."""

    values = [v.strip() for v in value.split(',')]
    if not all(values):
        raise ValueError('invalid value in the comma-separated list')

    return values


class NotificationFilterParameters(FilterParameters):
    """Query parameters for notifications filtering."""

    type: NotificationType | None = Query(default=None)
    recipient_username: str | None = Query(default=None)
    project_code_any: str | None = Query(default=None)
    created_at_start: datetime | None = Query(default=None)
    created_at_end: datetime | None = Query(default=None)

    @validator('project_code_any')
    def split_list_parameters(cls, value: str | None) -> list[str] | None:
        if not value:
            return None

        return split_list_parameters(value)

    def to_filtering(self) -> NotificationFiltering:
        return NotificationFiltering(
            type=self.type,
            recipient_username=self.recipient_username,
            project_code_any=self.project_code_any,
            created_at_start=self.created_at_start,
            created_at_end=self.created_at_end,
        )


class UserNotificationFilterParameters(FilterParameters):
    """Query parameters for user notifications filtering."""

    recipient_username: str = Query()
    project_code_any: str | None = Query()

    @validator('project_code_any')
    def split_list_parameters(cls, value: str) -> list[str]:
        if value:
            return split_list_parameters(value)
        return []

    def to_filtering(self) -> UserNotificationFiltering:
        return UserNotificationFiltering(
            recipient_username=self.recipient_username,
            project_code_any=self.project_code_any,
        )
