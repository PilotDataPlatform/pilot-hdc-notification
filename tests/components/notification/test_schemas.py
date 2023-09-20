# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from datetime import datetime
from typing import Annotated
from uuid import UUID

import pytest

from notification.components.notification import NotificationType
from notification.components.notification.models import CopyRequestAction
from notification.components.notification.models import InvolvementType
from notification.components.notification.models import PipelineAction
from notification.components.notification.models import PipelineStatus
from notification.components.notification.schemas import CopyRequestNotificationCreateSchema
from notification.components.notification.schemas import KeyField
from notification.components.notification.schemas import MaintenanceNotificationCreateSchema
from notification.components.notification.schemas import NotificationCreateSchema
from notification.components.notification.schemas import PipelineNotificationCreateSchema


class TestNotificationCreateSchema:
    def test_dict_returns_all_fields_except_annotated_with_key_field_in_nested_json_serialised_data_object(self, fake):
        class CustomNotificationCreateSchema(NotificationCreateSchema):
            recipient_username: Annotated[str, KeyField]
            some_id: UUID
            some_date: datetime

        schema = CustomNotificationCreateSchema(
            type=NotificationType.PIPELINE,
            recipient_username=fake.user_name(),
            some_id=fake.uuid4(None),
            some_date=fake.past_datetime_utc(),
        )

        expected_dict = {
            'type': schema.type.value,
            'recipient_username': schema.recipient_username,
            'data': {
                'some_id': str(schema.some_id),
                'some_date': schema.some_date.isoformat(),
            },
        }

        received_dict = schema.dict()

        assert received_dict == expected_dict


class TestPipelineNotificationCreateSchema:
    def test_destination_field_raises_value_error_for_none_value_when_action_is_copy(self, notification_factory):
        with pytest.raises(ValueError, match='invalid destination for copy action'):
            PipelineNotificationCreateSchema(
                recipient_username=notification_factory.generate_username(),
                involved_as=InvolvementType.OWNER,
                action=PipelineAction.COPY,
                status=PipelineStatus.SUCCESS,
                initiator_username=notification_factory.generate_username(),
                project_code=notification_factory.generate_project_code(),
                source=notification_factory.generate_location(),
                destination=None,
                targets=[notification_factory.generate_target()],
            )

    def test_destination_field_raises_value_error_for_not_none_value_when_action_is_delete(self, notification_factory):
        with pytest.raises(ValueError, match='invalid destination for delete action'):
            PipelineNotificationCreateSchema(
                recipient_username=notification_factory.generate_username(),
                involved_as=InvolvementType.OWNER,
                action=PipelineAction.DELETE,
                status=PipelineStatus.SUCCESS,
                initiator_username=notification_factory.generate_username(),
                project_code=notification_factory.generate_project_code(),
                source=notification_factory.generate_location(),
                destination=notification_factory.generate_location(),
                targets=[notification_factory.generate_target()],
            )

    def test_targets_field_raises_value_error_when_targets_field_is_empty(self, notification_factory):
        with pytest.raises(ValueError, match='ensure this value has at least 1 item'):
            PipelineNotificationCreateSchema(
                recipient_username=notification_factory.generate_username(),
                involved_as=InvolvementType.OWNER,
                action=PipelineAction.COPY,
                status=PipelineStatus.SUCCESS,
                initiator_username=notification_factory.generate_username(),
                project_code=notification_factory.generate_project_code(),
                source=notification_factory.generate_location(),
                destination=notification_factory.generate_location(),
                targets=[],
            )


class TestCopyRequestNotificationCreateSchema:
    @pytest.mark.parametrize('action', set(CopyRequestAction) - {CopyRequestAction.CLOSE})
    def test_source_field_raises_value_error_for_none_value_when_action_is_not_close(
        self, action, notification_factory
    ):
        with pytest.raises(ValueError, match=f'invalid source for {action.value} action'):
            CopyRequestNotificationCreateSchema(
                recipient_username=notification_factory.generate_username(),
                action=action,
                initiator_username=notification_factory.generate_username(),
                project_code=notification_factory.generate_project_code(),
                copy_request_id=notification_factory.generate_uuid(),
                source=None,
                destination=notification_factory.generate_location(),
                targets=[notification_factory.generate_target()],
            )

    @pytest.mark.parametrize('action', set(CopyRequestAction) - {CopyRequestAction.CLOSE})
    def test_destination_field_raises_value_error_for_none_value_when_action_is_not_close(
        self, action, notification_factory
    ):
        with pytest.raises(ValueError, match=f'invalid destination for {action.value} action'):
            CopyRequestNotificationCreateSchema(
                recipient_username=notification_factory.generate_username(),
                action=action,
                initiator_username=notification_factory.generate_username(),
                project_code=notification_factory.generate_project_code(),
                copy_request_id=notification_factory.generate_uuid(),
                source=notification_factory.generate_location(),
                destination=None,
                targets=[notification_factory.generate_target()],
            )

    @pytest.mark.parametrize('action', set(CopyRequestAction) - {CopyRequestAction.CLOSE})
    def test_targets_field_raises_value_error_for_none_value_when_action_is_not_close(
        self, action, notification_factory
    ):
        with pytest.raises(ValueError, match=f'invalid targets for {action.value} action'):
            CopyRequestNotificationCreateSchema(
                recipient_username=notification_factory.generate_username(),
                action=action,
                initiator_username=notification_factory.generate_username(),
                project_code=notification_factory.generate_project_code(),
                copy_request_id=notification_factory.generate_uuid(),
                source=notification_factory.generate_location(),
                destination=notification_factory.generate_location(),
                targets=None,
            )

    def test_targets_field_raises_value_error_when_targets_field_is_empty(self, notification_factory):
        with pytest.raises(ValueError, match='ensure this value has at least 1 item'):
            CopyRequestNotificationCreateSchema(
                recipient_username=notification_factory.generate_username(),
                action=CopyRequestAction.APPROVAL,
                initiator_username=notification_factory.generate_username(),
                project_code=notification_factory.generate_project_code(),
                copy_request_id=notification_factory.generate_uuid(),
                source=notification_factory.generate_location(),
                destination=notification_factory.generate_location(),
                targets=[],
            )


class TestMaintenanceNotificationCreateSchema:
    def test_effective_date_field_raises_value_error_when_date_is_not_offset_aware(self, fake):
        with pytest.raises(ValueError, match='ensure this date is offset-aware'):
            MaintenanceNotificationCreateSchema(
                announcement_id=fake.uuid4(None),
                effective_date=datetime.utcnow(),
                duration_minutes=fake.positive_int(),
                message=fake.sentence(),
            )
