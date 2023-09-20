# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from datetime import datetime
from typing import Any

import pytest

from notification.components.announcement.crud import AnnouncementCRUD
from notification.components.announcement.models import Announcement
from notification.components.announcement.schemas import AnnouncementCreateSchema
from notification.components.models import ModelList
from tests.fixtures.components._base_factory import BaseFactory


class AnnouncementFactory(BaseFactory):
    """Create announcement related entries for testing purposes."""

    def generate(
        self,
        *,
        effective_date: datetime = ...,
        duration_minutes: int = ...,
        message: str = ...,
    ) -> AnnouncementCreateSchema:
        if effective_date is ...:
            effective_date = self.fake.past_datetime_utc()

        if duration_minutes is ...:
            duration_minutes = self.fake.positive_int()

        if message is ...:
            message = self.fake.sentence()

        return AnnouncementCreateSchema(
            effective_date=effective_date, duration_minutes=duration_minutes, message=message
        )

    async def create(
        self,
        *,
        effective_date: datetime = ...,
        duration_minutes: int = ...,
        message: str = ...,
        **kwds: Any,
    ) -> Announcement:
        entry = self.generate(effective_date=effective_date, duration_minutes=duration_minutes, message=message)

        return await self.crud.create(entry, **kwds)

    async def bulk_create(
        self,
        number: int,
        *,
        effective_date: datetime = ...,
        duration_minutes: int = ...,
        message: str = ...,
        **kwds: Any,
    ) -> ModelList[Announcement]:
        return ModelList(
            [
                await self.create(
                    effective_date=effective_date,
                    duration_minutes=duration_minutes,
                    message=message,
                    **kwds,
                )
                for _ in range(number)
            ]
        )


@pytest.fixture
def announcement_crud(db_session) -> AnnouncementCRUD:
    yield AnnouncementCRUD(db_session)


@pytest.fixture
async def announcement_factory(announcement_crud, fake) -> AnnouncementFactory:
    announcement_factory = AnnouncementFactory(announcement_crud, fake)
    yield announcement_factory
    await announcement_factory.truncate_table()
