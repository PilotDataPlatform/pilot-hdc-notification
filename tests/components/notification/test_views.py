# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import random
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from enum import Enum

import pytest

from notification.components.notification.parameters import NotificationSortByFields
from notification.components.sorting import SortingOrder


class TestNotificationViews:
    async def test_list_notifications_returns_list_of_different_notifications(self, client, jq, notification_factory):
        notifications = await notification_factory.create_all_available()

        expected_notification_ids = notifications.get_field_values('id', str)
        expected_notification_types = notifications.get_field_values('type')

        response = await client.get('/v1/all/notifications/')

        assert response.status_code == 200

        body = jq(response)
        received_total = body('.total').first()
        assert received_total == len(notifications)

        received_notification_ids = body('.result[].id').all()
        assert set(received_notification_ids) == set(expected_notification_ids)

        received_notification_types = body('.result[].type').all()
        assert set(received_notification_types) == set(expected_notification_types)

    @pytest.mark.parametrize(
        'items_number,page,page_size,expected_count',
        [
            (4, 1, 3, 3),
            (4, 2, 3, 1),
            (2, 1, 3, 2),
            (2, 2, 1, 1),
            (2, 3, 1, 0),
            (3, 1, 0, 3),
        ],
    )
    async def test_list_notifications_returns_properly_paginated_response(
        self, items_number, page, page_size, expected_count, client, jq, notification_factory
    ):
        await notification_factory.bulk_create_pipeline(items_number)

        response = await client.get('/v1/all/notifications/', params={'page': page, 'page_size': page_size})

        assert response.status_code == 200

        body = jq(response)
        received_notification_ids = body('.result[].id').all()
        received_total = body('.total').first()

        assert len(received_notification_ids) == expected_count
        assert received_total == items_number

    @pytest.mark.parametrize('sort_by', NotificationSortByFields.values())
    @pytest.mark.parametrize('sort_order', SortingOrder.values())
    async def test_list_notifications_returns_results_sorted_by_field_with_proper_order(
        self, sort_by, sort_order, client, jq, notification_factory
    ):
        created_notifications = await notification_factory.bulk_create_pipeline(3)
        field_values = created_notifications.get_field_values(sort_by)
        if sort_by == 'created_at':
            field_values = [key.isoformat() for key in field_values]
        expected_values = sorted(field_values, reverse=sort_order == SortingOrder.DESC)

        response = await client.get('/v1/all/notifications/', params={'sort_by': sort_by, 'sort_order': sort_order})

        assert response.status_code == 200

        body = jq(response)
        received_values = body(f'.result[].{sort_by}').all()
        received_total = body('.total').first()

        assert received_values == expected_values
        assert received_total == 3

    @pytest.mark.parametrize('parameter', ['type', 'recipient_username'])
    async def test_list_notifications_returns_list_of_notifications_filtered_by_parameter_full_text_match(
        self, parameter, client, jq, notification_factory
    ):
        created_notifications = await notification_factory.create_all_available()
        notification = random.choice(created_notifications)
        value = getattr(notification, parameter)
        expected_notification_ids = [
            str(notification.id) for notification in created_notifications if getattr(notification, parameter) == value
        ]
        if isinstance(value, Enum):
            value = value.value

        response = await client.get('/v1/all/notifications/', params={parameter: value or ''})

        assert response.status_code == 200

        body = jq(response)
        received_notification_ids = body('.result[].id').all()

        assert sorted(received_notification_ids) == sorted(expected_notification_ids)

    async def test_list_notifications_returns_list_of_notifications_filtered_by_project_code_any_parameter(
        self, client, jq, notification_factory
    ):
        created_projects = await notification_factory.bulk_create_project(3)
        project_codes = created_projects.get_field_values('project_code')
        project_codes = random.sample(project_codes, 2)

        response = await client.get('/v1/all/notifications/', params={'project_code_any': ','.join(project_codes)})

        body = jq(response)
        received_project_codes = body('.result[].project_code').all()
        received_total = body('.total').first()

        assert set(received_project_codes) == set(project_codes)
        assert received_total == 2

    async def test_list_notifications_returns_list_of_notifications_filtered_by_created_at_parameters(
        self, client, jq, fake, notification_factory
    ):
        today = datetime.now(tz=timezone.utc)
        week_ago = today - timedelta(days=7)
        two_weeks_ago = today - timedelta(days=14)

        [
            await notification_factory.create_maintenance(
                created_at=fake.date_time_between_dates(two_weeks_ago, week_ago)
            )
            for _ in range(2)
        ]
        project_notification = await notification_factory.create_project(
            created_at=fake.date_time_between_dates(week_ago, today)
        )

        response = await client.get(
            '/v1/all/notifications/',
            params={
                'created_at_start': int(datetime.timestamp(week_ago)),
                'created_at_end': int(datetime.timestamp(today)),
            },
        )

        body = jq(response)
        received_notification_ids = body('.result[].id').all()
        received_total = body('.total').first()

        assert received_notification_ids == [str(project_notification.id)]
        assert received_total == 1

    async def test_list_notifications_returns_list_of_notifications_filtered_considering_query_parameters(
        self, client, jq, notification_factory
    ):
        created_pipelines = await notification_factory.bulk_create_pipeline(2)
        created_projects = await notification_factory.bulk_create_project(2)
        created_maintenances = await notification_factory.bulk_create_maintenance(2)
        pipeline_notification = random.choice(created_pipelines)
        project_notification = random.choice(created_projects)
        expected_notification_ids = [
            str(pipeline_notification.id),
            str(project_notification.id),
        ] + created_maintenances.get_field_values('id', str)

        response = await client.get(
            '/v1/all/notifications/user',
            params={
                'recipient_username': pipeline_notification.recipient_username,
                'project_code_any': project_notification.project_code,
            },
        )

        body = jq(response)
        received_notification_ids = body('.result[].id').all()
        received_total = body('.total').first()

        assert set(received_notification_ids) == set(expected_notification_ids)
        assert received_total == 4

    @pytest.mark.parametrize(
        'factory_method,notification_field',
        [
            ('generate_pipeline', 'initiator_username'),
            ('generate_copy_request', 'copy_request_id'),
            ('generate_role_change', 'previous'),
            ('generate_project', 'project_name'),
            ('generate_maintenance', 'effective_date'),
        ],
    )
    async def test_create_notification_creates_single_notification(
        self, factory_method, notification_field, client, notification_factory, notification_crud
    ):
        notification = getattr(notification_factory, factory_method)()
        expected_field = getattr(notification, notification_field)

        payload = notification.to_payload()
        response = await client.post('/v1/all/notifications/', json=payload)

        assert response.status_code == 204

        received_notifications = await notification_crud.list()

        assert len(received_notifications) == 1
        assert received_notifications[0].type == notification.type

        received_field = getattr(received_notifications[0], notification_field)
        assert received_field == expected_field

    @pytest.mark.parametrize(
        'factory_method,notification_field',
        [
            ('generate_pipeline', 'action'),
            ('generate_copy_request', 'action'),
            ('generate_role_change', 'current'),
            ('generate_project', 'announcer_username'),
            ('generate_maintenance', 'duration_minutes'),
        ],
    )
    async def test_create_notification_creates_multiple_notifications(
        self, factory_method, notification_field, client, notification_factory, notification_crud
    ):
        method = getattr(notification_factory, factory_method)
        notification_1 = method()
        notification_2 = method()
        expected_notification_fields = {
            getattr(notification_1, notification_field),
            getattr(notification_2, notification_field),
        }

        payload = [notification_1.to_payload(), notification_2.to_payload()]
        response = await client.post('/v1/all/notifications/', json=payload)

        assert response.status_code == 204

        received_notifications = await notification_crud.list()

        assert len(received_notifications) == 2

        received_notification_types = received_notifications.get_field_values('type')
        assert set(received_notification_types) == {notification_1.type, notification_2.type}

        received_notification_fields = received_notifications.get_field_values(notification_field)
        assert set(received_notification_fields) == expected_notification_fields

    async def test_create_notification_creates_multiple_different_notifications_in_one_payload(
        self, client, notification_factory, notification_crud
    ):
        notifications = notification_factory.generate_all_available()

        expected_notification_types = notifications.get_field_values('type')

        payload = [notification.to_payload() for notification in notifications]
        response = await client.post('/v1/all/notifications/', json=payload)

        assert response.status_code == 204

        received_notifications = await notification_crud.list()

        assert len(received_notifications) == len(notifications)

        received_notification_types = received_notifications.get_field_values('type')
        assert set(received_notification_types) == set(expected_notification_types)
