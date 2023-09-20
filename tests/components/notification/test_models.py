# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from datetime import datetime
from uuid import UUID

import pytest

from notification.components.notification import CopyRequestNotification
from notification.components.notification import PipelineNotification


class TestNotification:
    @pytest.mark.parametrize(
        'factory_method',
        [
            'generate_pipeline',
            'generate_copy_request',
            'generate_role_change',
            'generate_project',
        ],
    )
    async def test_each_derived_notification_model_returns_values_for_all_fields_in_creation_schema(
        self, factory_method, notification_factory
    ):
        notification = getattr(notification_factory, factory_method)()
        created_notification = await notification_factory.crud.create(notification)

        assert isinstance(created_notification.id, UUID)
        assert isinstance(created_notification.created_at, datetime)

        assert list(notification)
        for key, value in notification:
            assert getattr(created_notification, key) == value


class TestPipelineNotification:
    def test_destination_returns_none_when_destination_in_data_is_none(self):
        pipeline_notification = PipelineNotification(data={'destination': None})

        assert pipeline_notification.destination is None


class TestCopyRequestNotification:
    @pytest.mark.parametrize('field', ['source', 'destination', 'targets'])
    def test_field_returns_none_when_value_in_data_is_none(self, field):
        copy_request_notification = CopyRequestNotification(data={field: None})

        assert getattr(copy_request_notification, field) is None
