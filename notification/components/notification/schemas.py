# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from datetime import datetime
from typing import Annotated
from typing import Any
from typing import Literal
from uuid import UUID

from pydantic import Field
from pydantic import PositiveInt
from pydantic import conlist
from pydantic import validator
from pydantic.fields import ModelField

from notification.components.notification.models import CopyRequestAction
from notification.components.notification.models import InvolvementType
from notification.components.notification.models import Location
from notification.components.notification.models import NotificationType
from notification.components.notification.models import PipelineAction
from notification.components.notification.models import PipelineStatus
from notification.components.notification.models import Target
from notification.components.schemas import BaseSchema
from notification.components.schemas import ListResponseSchema


class KeyField:
    """Annotation type for fields that must be serialised as top level keys."""


class NotificationSchema(BaseSchema):
    """General notification schema."""

    type: Annotated[NotificationType, KeyField]


class NotificationCreateSchema(NotificationSchema):
    """General schema used for notification creation."""

    def dict(self, **kwds: Any) -> dict[str, Any]:
        """Generate a dictionary representation of the model with JSON serialisable values.

        Fields annotated with `KeyField` will be used as keys. All the remaining fields will be nested under `data` key.
        """

        json = super().json(**kwds)
        obj = self.__config__.json_loads(json)

        data = {'data': obj}
        root_fields = self.get_fields_annotated_with(KeyField)
        for field in root_fields:
            data[field] = obj.pop(field)

        return data


class PipelineNotificationCreateSchema(NotificationCreateSchema):
    """Schema for pipeline notification creation."""

    type: Annotated[Literal[NotificationType.PIPELINE], KeyField] = NotificationType.PIPELINE
    recipient_username: Annotated[str, KeyField]
    involved_as: InvolvementType
    action: PipelineAction
    status: PipelineStatus
    initiator_username: str
    project_code: Annotated[str, KeyField]
    source: Location
    destination: Location | None
    targets: conlist(Target, min_items=1)

    @validator('destination')
    def is_valid_destination_for_action(cls, value: Location | None, values: dict[str, Any]) -> Location | None:
        if value is None and values['action'] is PipelineAction.COPY:
            raise ValueError('invalid destination for copy action')

        if value is not None and values['action'] is PipelineAction.DELETE:
            raise ValueError('invalid destination for delete action')

        return value


class CopyRequestNotificationCreateSchema(NotificationCreateSchema):
    """Schema for copy request notification creation."""

    type: Annotated[Literal[NotificationType.COPY_REQUEST], KeyField] = NotificationType.COPY_REQUEST
    recipient_username: Annotated[str, KeyField]
    action: CopyRequestAction
    initiator_username: str
    project_code: Annotated[str, KeyField]
    copy_request_id: UUID
    source: Location | None
    destination: Location | None
    targets: conlist(Target, min_items=1) | None

    @validator('source', 'destination', 'targets')
    def validate_fields_dependent_on_action(
        cls, value: Location | list[Target] | None, values: dict[str, Any], field: ModelField
    ) -> Location | list[Target] | None:
        action = values['action']

        is_invalid = value is None
        if action is CopyRequestAction.CLOSE:
            is_invalid = value is not None

        if is_invalid:
            raise ValueError(f'invalid {field.name} for {action.value} action')

        return value


class RoleChangeNotificationCreateSchema(NotificationCreateSchema):
    """Schema for role change notification creation."""

    type: Annotated[Literal[NotificationType.ROLE_CHANGE], KeyField] = NotificationType.ROLE_CHANGE
    recipient_username: Annotated[str, KeyField]
    initiator_username: str
    project_code: Annotated[str, KeyField]
    previous: str
    current: str


class ProjectNotificationCreateSchema(NotificationCreateSchema):
    """Schema for project notification creation."""

    type: Annotated[Literal[NotificationType.PROJECT], KeyField] = NotificationType.PROJECT
    project_code: Annotated[str, KeyField]
    project_name: str
    announcer_username: str
    message: str


class MaintenanceNotificationCreateSchema(NotificationCreateSchema):
    """Schema for maintenance notification creation."""

    type: Annotated[Literal[NotificationType.MAINTENANCE], KeyField] = NotificationType.MAINTENANCE
    announcement_id: UUID
    effective_date: datetime
    duration_minutes: PositiveInt
    message: str

    @validator('effective_date')
    def is_timezone_aware(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError('ensure this date is offset-aware')

        return value


NotificationsCreateSchema = Annotated[
    PipelineNotificationCreateSchema
    | CopyRequestNotificationCreateSchema
    | RoleChangeNotificationCreateSchema
    | ProjectNotificationCreateSchema
    | MaintenanceNotificationCreateSchema,
    Field(discriminator='type'),
]


class NotificationResponseSchema(NotificationSchema):
    """Default schema for single notification in response."""

    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class PipelineNotificationResponseSchema(NotificationResponseSchema):
    """Schema for single pipeline notification in response."""

    type: Literal[NotificationType.PIPELINE]
    recipient_username: str
    involved_as: InvolvementType
    action: PipelineAction
    status: PipelineStatus
    initiator_username: str
    project_code: str
    source: Location
    destination: Location | None
    targets: list[Target]


class CopyRequestNotificationResponseSchema(NotificationResponseSchema):
    """Schema for single copy request notification in response."""

    type: Literal[NotificationType.COPY_REQUEST]
    recipient_username: str
    action: CopyRequestAction
    initiator_username: str
    project_code: str
    copy_request_id: UUID
    source: Location | None
    destination: Location | None
    targets: list[Target] | None


class RoleChangeNotificationResponseSchema(NotificationResponseSchema):
    """Schema for single role change notification in response."""

    type: Literal[NotificationType.ROLE_CHANGE]
    recipient_username: str
    initiator_username: str
    project_code: str
    previous: str
    current: str


class ProjectNotificationResponseSchema(NotificationResponseSchema):
    """Schema for single project notification in response."""

    type: Literal[NotificationType.PROJECT]
    project_code: str
    project_name: str
    announcer_username: str
    message: str


class MaintenanceNotificationResponseSchema(NotificationResponseSchema):
    """Schema for single maintenance notification in response."""

    type: Literal[NotificationType.MAINTENANCE]
    announcement_id: UUID
    effective_date: datetime
    duration_minutes: int
    message: str


NotificationsResponseSchema = Annotated[
    PipelineNotificationResponseSchema
    | CopyRequestNotificationResponseSchema
    | RoleChangeNotificationResponseSchema
    | ProjectNotificationResponseSchema
    | MaintenanceNotificationResponseSchema,
    Field(discriminator='type'),
]


class NotificationListResponseSchema(ListResponseSchema):
    """Default schema for multiple notifications in response."""

    result: list[NotificationsResponseSchema]
