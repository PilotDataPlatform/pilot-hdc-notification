# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import random
from datetime import datetime
from typing import Any
from uuid import UUID

import pytest

from notification.components.models import ModelList
from notification.components.notification import CopyRequestNotification
from notification.components.notification import PipelineNotification
from notification.components.notification import ProjectNotification
from notification.components.notification import RoleChangeNotification
from notification.components.notification.crud import NotificationCRUD
from notification.components.notification.models import CopyRequestAction
from notification.components.notification.models import InvolvementType
from notification.components.notification.models import Location
from notification.components.notification.models import MaintenanceNotification
from notification.components.notification.models import Notification
from notification.components.notification.models import PipelineAction
from notification.components.notification.models import PipelineStatus
from notification.components.notification.models import Target
from notification.components.notification.models import TargetType
from notification.components.notification.schemas import CopyRequestNotificationCreateSchema
from notification.components.notification.schemas import MaintenanceNotificationCreateSchema
from notification.components.notification.schemas import NotificationCreateSchema
from notification.components.notification.schemas import PipelineNotificationCreateSchema
from notification.components.notification.schemas import ProjectNotificationCreateSchema
from notification.components.notification.schemas import RoleChangeNotificationCreateSchema
from tests.fixtures.components._base_factory import BaseFactory


class NotificationFactory(BaseFactory):
    """Create notification related entries for testing purposes."""

    def generate_all_available(self) -> ModelList[NotificationCreateSchema]:
        methods = {
            'generate_pipeline',
            'generate_copy_request',
            'generate_role_change',
            'generate_project',
            'generate_maintenance',
        }
        return ModelList([getattr(self, method)() for method in methods])

    def generate_pipeline(  # noqa: C901
        self,
        *,
        recipient_username: str = ...,
        involved_as: InvolvementType = ...,
        action: PipelineAction = ...,
        status: PipelineStatus = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        source: Location = ...,
        destination: Location | None = ...,
        targets: list[Target] = ...,
    ) -> PipelineNotificationCreateSchema:
        if recipient_username is ...:
            recipient_username = self.generate_username()

        if involved_as is ...:
            involved_as = random.choice(list(InvolvementType))

        if action is ...:
            action = random.choice(list(PipelineAction))

        if status is ...:
            status = random.choice(list(PipelineStatus))

        if initiator_username is ...:
            initiator_username = self.generate_username()

        if project_code is ...:
            project_code = self.generate_project_code()

        if source is ...:
            source = self.generate_location()

        if destination is ...:
            destination = self.generate_location()
            if action is PipelineAction.DELETE:
                destination = None

        if targets is ...:
            targets = [self.generate_target() for _ in range(self.fake.pyint(1, 3))]

        return PipelineNotificationCreateSchema(
            recipient_username=recipient_username,
            involved_as=involved_as,
            action=action,
            status=status,
            initiator_username=initiator_username,
            project_code=project_code,
            source=source,
            destination=destination,
            targets=targets,
        )

    def generate_copy_request(
        self,
        *,
        recipient_username: str = ...,
        action: CopyRequestAction = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        copy_request_id: UUID = ...,
        source: Location | None = ...,
        destination: Location | None = ...,
        targets: list[Target] | None = ...,
    ) -> CopyRequestNotificationCreateSchema:
        if recipient_username is ...:
            recipient_username = self.generate_username()

        if action is ...:
            action = random.choice(list(CopyRequestAction))

        if initiator_username is ...:
            initiator_username = self.generate_username()

        if project_code is ...:
            project_code = self.generate_project_code()

        if copy_request_id is ...:
            copy_request_id = self.generate_uuid()

        if source is ...:
            source = self.generate_location()

        if destination is ...:
            destination = self.generate_location()

        if targets is ...:
            targets = [self.generate_target() for _ in range(self.fake.pyint(1, 3))]

        if action is CopyRequestAction.CLOSE:
            source = destination = targets = None

        return CopyRequestNotificationCreateSchema(
            recipient_username=recipient_username,
            action=action,
            initiator_username=initiator_username,
            project_code=project_code,
            copy_request_id=copy_request_id,
            source=source,
            destination=destination,
            targets=targets,
        )

    def generate_role_change(
        self,
        *,
        recipient_username: str = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        previous: str = ...,
        current: str = ...,
    ) -> RoleChangeNotificationCreateSchema:
        if recipient_username is ...:
            recipient_username = self.generate_username()

        if initiator_username is ...:
            initiator_username = self.generate_username()

        if project_code is ...:
            project_code = self.generate_project_code()

        if previous is ...:
            previous = self.fake.unique.user_name().lower()

        if current is ...:
            current = self.fake.unique.user_name().lower()

        return RoleChangeNotificationCreateSchema(
            recipient_username=recipient_username,
            initiator_username=initiator_username,
            project_code=project_code,
            previous=previous,
            current=current,
        )

    def generate_project(
        self,
        *,
        project_code: str = ...,
        project_name: str = ...,
        announcer_username: str = ...,
        message: str = ...,
    ) -> ProjectNotificationCreateSchema:
        if project_code is ...:
            project_code = self.generate_project_code()

        if project_name is ...:
            project_name = self.fake.sentence()

        if announcer_username is ...:
            announcer_username = self.generate_username()

        if message is ...:
            message = self.fake.sentence()

        return ProjectNotificationCreateSchema(
            project_code=project_code,
            project_name=project_name,
            announcer_username=announcer_username,
            message=message,
        )

    def generate_maintenance(
        self,
        *,
        announcement_id: UUID = ...,
        effective_date: datetime = ...,
        duration_minutes: int = ...,
        message: str = ...,
    ) -> MaintenanceNotificationCreateSchema:
        if announcement_id is ...:
            announcement_id = self.generate_uuid()

        if effective_date is ...:
            effective_date = self.fake.past_datetime_utc()

        if duration_minutes is ...:
            duration_minutes = self.fake.positive_int()

        if message is ...:
            message = self.fake.sentence()

        return MaintenanceNotificationCreateSchema(
            announcement_id=announcement_id,
            effective_date=effective_date,
            duration_minutes=duration_minutes,
            message=message,
        )

    def generate_username(self) -> str:
        return self.fake.unique.user_name().lower()

    def generate_project_code(self) -> str:
        return self.fake.pystr_format('?#' * 10).lower()

    def generate_uuid(self) -> UUID:
        return self.fake.uuid4(None)

    def generate_zone(self) -> int:
        return self.fake.pyint(0, 1)

    def generate_location(self) -> Location:
        location_path = '/'.join(self.fake.words(3)).lower()
        return Location(id=self.generate_uuid(), path=location_path, zone=self.generate_zone())

    def generate_target(self) -> Target:
        target_type = random.choice(list(TargetType))

        target_name = self.fake.unique.file_name().lower()
        if target_type is TargetType.FOLDER:
            target_name = self.fake.unique.word().lower()

        return Target(id=self.generate_uuid(), type=target_type, name=target_name)

    async def create_all_available(self) -> ModelList[Notification]:
        methods = {
            'create_pipeline',
            'create_copy_request',
            'create_role_change',
            'create_project',
            'create_maintenance',
        }
        return ModelList([await getattr(self, method)() for method in methods])

    async def create_pipeline(
        self,
        *,
        recipient_username: str = ...,
        involved_as: InvolvementType = ...,
        action: PipelineAction = ...,
        status: PipelineStatus = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        source: Location = ...,
        destination: Location | None = ...,
        targets: list[Target] = ...,
        **kwds: Any,
    ) -> PipelineNotification:
        entry = self.generate_pipeline(
            recipient_username=recipient_username,
            involved_as=involved_as,
            action=action,
            status=status,
            initiator_username=initiator_username,
            project_code=project_code,
            source=source,
            destination=destination,
            targets=targets,
        )

        return await self.crud.create(entry, **kwds)

    async def create_copy_request(
        self,
        *,
        recipient_username: str = ...,
        action: CopyRequestAction = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        copy_request_id: UUID = ...,
        source: Location | None = ...,
        destination: Location | None = ...,
        targets: list[Target] | None = ...,
        **kwds: Any,
    ) -> CopyRequestNotification:
        entry = self.generate_copy_request(
            recipient_username=recipient_username,
            action=action,
            initiator_username=initiator_username,
            project_code=project_code,
            copy_request_id=copy_request_id,
            source=source,
            destination=destination,
            targets=targets,
        )

        return await self.crud.create(entry, **kwds)

    async def create_role_change(
        self,
        *,
        recipient_username: str = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        previous: str = ...,
        current: str = ...,
        **kwds: Any,
    ) -> RoleChangeNotification:
        entry = self.generate_role_change(
            recipient_username=recipient_username,
            initiator_username=initiator_username,
            project_code=project_code,
            previous=previous,
            current=current,
        )

        return await self.crud.create(entry, **kwds)

    async def create_project(
        self,
        *,
        project_code: str = ...,
        project_name: str = ...,
        announcer_username: str = ...,
        message: str = ...,
        **kwds: Any,
    ) -> ProjectNotification:
        entry = self.generate_project(
            project_code=project_code,
            project_name=project_name,
            announcer_username=announcer_username,
            message=message,
        )

        return await self.crud.create(entry, **kwds)

    async def create_maintenance(
        self,
        *,
        announcement_id: UUID = ...,
        effective_date: datetime = ...,
        duration_minutes: int = ...,
        message: str = ...,
        **kwds: Any,
    ) -> MaintenanceNotification:
        entry = self.generate_maintenance(
            announcement_id=announcement_id,
            effective_date=effective_date,
            duration_minutes=duration_minutes,
            message=message,
        )

        return await self.crud.create(entry, **kwds)

    async def bulk_create_pipeline(
        self,
        number: int,
        *,
        recipient_username: str = ...,
        involved_as: InvolvementType = ...,
        action: PipelineAction = ...,
        status: PipelineStatus = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        source: Location = ...,
        destination: Location | None = ...,
        targets: list[Target] = ...,
        **kwds: Any,
    ) -> ModelList[PipelineNotification]:
        return ModelList(
            [
                await self.create_pipeline(
                    recipient_username=recipient_username,
                    involved_as=involved_as,
                    action=action,
                    status=status,
                    initiator_username=initiator_username,
                    project_code=project_code,
                    source=source,
                    destination=destination,
                    targets=targets,
                    **kwds,
                )
                for _ in range(number)
            ]
        )

    async def bulk_create_copy_request(
        self,
        number: int,
        *,
        recipient_username: str = ...,
        action: CopyRequestAction = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        copy_request_id: UUID = ...,
        source: Location | None = ...,
        destination: Location | None = ...,
        targets: list[Target] | None = ...,
        **kwds: Any,
    ) -> ModelList[CopyRequestNotification]:
        return ModelList(
            [
                await self.create_copy_request(
                    recipient_username=recipient_username,
                    action=action,
                    initiator_username=initiator_username,
                    project_code=project_code,
                    copy_request_id=copy_request_id,
                    source=source,
                    destination=destination,
                    targets=targets,
                    **kwds,
                )
                for _ in range(number)
            ]
        )

    async def bulk_create_role_change(
        self,
        number: int,
        *,
        recipient_username: str = ...,
        initiator_username: str = ...,
        project_code: str = ...,
        previous: str = ...,
        current: str = ...,
        **kwds: Any,
    ) -> ModelList[RoleChangeNotification]:
        return ModelList(
            [
                await self.create_role_change(
                    recipient_username=recipient_username,
                    initiator_username=initiator_username,
                    project_code=project_code,
                    previous=previous,
                    current=current,
                    **kwds,
                )
                for _ in range(number)
            ]
        )

    async def bulk_create_project(
        self,
        number: int,
        *,
        project_code: str = ...,
        project_name: str = ...,
        announcer_username: str = ...,
        message: str = ...,
        **kwds: Any,
    ) -> ModelList[ProjectNotification]:
        return ModelList(
            [
                await self.create_project(
                    project_code=project_code,
                    project_name=project_name,
                    announcer_username=announcer_username,
                    message=message,
                    **kwds,
                )
                for _ in range(number)
            ]
        )

    async def bulk_create_maintenance(
        self,
        number: int,
        *,
        announcement_id: UUID = ...,
        effective_date: datetime = ...,
        duration_minutes: int = ...,
        message: str = ...,
        **kwds: Any,
    ) -> ModelList[MaintenanceNotification]:
        return ModelList(
            [
                await self.create_maintenance(
                    announcement_id=announcement_id,
                    effective_date=effective_date,
                    duration_minutes=duration_minutes,
                    message=message,
                    **kwds,
                )
                for _ in range(number)
            ]
        )


@pytest.fixture
def notification_crud(db_session) -> NotificationCRUD:
    yield NotificationCRUD(db_session)


@pytest.fixture
async def notification_factory(notification_crud, fake) -> NotificationFactory:
    notification_factory = NotificationFactory(notification_crud, fake)
    yield notification_factory
    await notification_factory.truncate_table()
