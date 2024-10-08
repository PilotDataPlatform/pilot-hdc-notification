# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from datetime import datetime
from uuid import UUID

from pydantic import PositiveInt
from pydantic import constr

from notification.components.schemas import BaseSchema
from notification.components.schemas import ListResponseSchema
from notification.components.schemas import ParentOptionalFields


class AnnouncementSchema(BaseSchema):
    """General announcement schema."""

    effective_date: datetime
    duration_minutes: PositiveInt
    message: constr(min_length=3, max_length=512)


class AnnouncementCreateSchema(AnnouncementSchema):
    """Announcement schema used for creation."""


class AnnouncementUpdateSchema(AnnouncementSchema, metaclass=ParentOptionalFields):
    """Announcement schema used for update."""


class AnnouncementResponseSchema(AnnouncementSchema):
    """Default schema for single announcement in response."""

    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class AnnouncementListResponseSchema(ListResponseSchema):
    """Default schema for multiple announcements in response."""

    result: list[AnnouncementResponseSchema]


class AnnouncementUnsubscriptionCreateSchema(BaseSchema):
    """Announcement unsubscription schema used for unsubscribing user from announcement."""

    username: constr(min_length=3, max_length=256)
