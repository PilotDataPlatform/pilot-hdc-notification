# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from datetime import datetime
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import VARCHAR
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func

from notification.components.db_model import DBModel
from notification.components.types import StrEnum


class NotificationType(StrEnum):
    """Available notification types."""

    PIPELINE = 'pipeline'
    COPY_REQUEST = 'copy-request'
    ROLE_CHANGE = 'role-change'
    PROJECT = 'project'
    MAINTENANCE = 'maintenance'


class TargetType(StrEnum):
    """Available target types."""

    FILE = 'file'
    FOLDER = 'folder'


class Target(BaseModel):
    """Model for file/folder object in notification."""

    id: UUID
    type: TargetType
    name: str


class Location(BaseModel):
    """Model for source/destination folder object in notification."""

    id: UUID
    path: str
    zone: int


class PipelineAction(StrEnum):
    """Available pipeline actions."""

    DELETE = 'delete'
    COPY = 'copy'


class PipelineStatus(StrEnum):
    """Available pipeline statuses."""

    SUCCESS = 'success'
    FAILURE = 'failure'


class InvolvementType(StrEnum):
    """Available involvement types."""

    INITIATOR = 'initiator'
    OWNER = 'owner'
    RECEIVER = 'receiver'


class CopyRequestAction(StrEnum):
    """Available copy request actions."""

    APPROVAL = 'approval'
    DENIAL = 'denial'
    CLOSE = 'close'


class Notification(DBModel):
    """Notification database model."""

    __tablename__ = 'notifications'
    __mapper_args__ = {'polymorphic_on': 'type'}

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(
        ENUM(NotificationType, name='notification_type', values_callable=lambda enum: enum.values()),
        nullable=False,
        index=True,
    )
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False, index=True)
    recipient_username = Column(VARCHAR(length=256), nullable=True, index=True)
    project_code = Column(VARCHAR(length=32), nullable=True, index=True)
    data = Column(JSONB(), nullable=False)


class PipelineNotification(Notification):
    """Pipeline notification database model."""

    __mapper_args__ = {'polymorphic_identity': NotificationType.PIPELINE}

    @property
    def involved_as(self) -> InvolvementType:
        return InvolvementType(self.data['involved_as'])

    @property
    def action(self) -> PipelineAction:
        return PipelineAction(self.data['action'])

    @property
    def status(self) -> PipelineStatus:
        return PipelineStatus(self.data['status'])

    @property
    def initiator_username(self) -> str:
        return self.data['initiator_username']

    @property
    def source(self) -> Location:
        return Location.parse_obj(self.data['source'])

    @property
    def destination(self) -> Location | None:
        if self.data['destination'] is None:
            return None

        return Location.parse_obj(self.data['destination'])

    @property
    def targets(self) -> list[Target]:
        return [Target.parse_obj(target) for target in self.data['targets']]


class CopyRequestNotification(Notification):
    """Copy request notification database model."""

    __mapper_args__ = {'polymorphic_identity': NotificationType.COPY_REQUEST}

    @property
    def action(self) -> CopyRequestAction:
        return CopyRequestAction(self.data['action'])

    @property
    def initiator_username(self) -> str:
        return self.data['initiator_username']

    @property
    def copy_request_id(self) -> UUID:
        return UUID(self.data['copy_request_id'])

    @property
    def source(self) -> Location | None:
        if self.data['source'] is None:
            return None

        return Location.parse_obj(self.data['source'])

    @property
    def destination(self) -> Location | None:
        if self.data['destination'] is None:
            return None

        return Location.parse_obj(self.data['destination'])

    @property
    def targets(self) -> list[Target] | None:
        if self.data['targets'] is None:
            return None

        return [Target.parse_obj(target) for target in self.data['targets']]


class RoleChangeNotification(Notification):
    """Role change notification database model."""

    __mapper_args__ = {'polymorphic_identity': NotificationType.ROLE_CHANGE}

    @property
    def initiator_username(self) -> str:
        return self.data['initiator_username']

    @property
    def previous(self) -> str:
        return self.data['previous']

    @property
    def current(self) -> str:
        return self.data['current']


class ProjectNotification(Notification):
    """Project notification database model."""

    __mapper_args__ = {'polymorphic_identity': NotificationType.PROJECT}

    @property
    def project_name(self) -> str:
        return self.data['project_name']

    @property
    def announcer_username(self) -> str:
        return self.data['announcer_username']

    @property
    def message(self) -> str:
        return self.data['message']


class MaintenanceNotification(Notification):
    """Maintenance notification database model."""

    __mapper_args__ = {'polymorphic_identity': NotificationType.MAINTENANCE}

    @property
    def announcement_id(self) -> UUID:
        return UUID(self.data['announcement_id'])

    @property
    def effective_date(self) -> datetime:
        return datetime.fromisoformat(self.data['effective_date'])

    @property
    def duration_minutes(self) -> int:
        return self.data['duration_minutes']

    @property
    def message(self) -> str:
        return self.data['message']
