# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

import pytest

from notification.components.announcement.parameters import AnnouncementSortByFields
from notification.components.announcement.schemas import AnnouncementUnsubscriptionCreateSchema
from notification.components.exceptions import NotFound
from notification.components.sorting import SortingOrder


class TestAnnouncementViews:
    async def test_list_announcements_returns_list_of_existing_announcements(self, client, jq, announcement_factory):
        created_announcement = await announcement_factory.create()

        response = await client.get('/v2/announcements/')

        assert response.status_code == 200

        body = jq(response)
        received_announcement_id = body('.result[].id').first()
        received_total = body('.total').first()

        assert received_announcement_id == str(created_announcement.id)
        assert received_total == 1

    @pytest.mark.parametrize('sort_by', AnnouncementSortByFields.values())
    @pytest.mark.parametrize('sort_order', SortingOrder.values())
    async def test_list_announcements_returns_results_sorted_by_field_with_proper_order(
        self, sort_by, sort_order, client, jq, announcement_factory
    ):
        created_announcements = await announcement_factory.bulk_create(3)
        field_values = created_announcements.get_field_values(sort_by)
        if sort_by in {'effective_date', 'created_at'}:
            field_values = [key.isoformat() for key in field_values]
        expected_values = sorted(field_values, reverse=sort_order == SortingOrder.DESC)

        response = await client.get('/v2/announcements/', params={'sort_by': sort_by, 'sort_order': sort_order})

        body = jq(response)
        received_values = body(f'.result[].{sort_by}').all()
        received_total = body('.total').first()

        assert received_values == expected_values
        assert received_total == 3

    async def test_list_announcements_returns_list_of_announcements_excluding_unsubscribed_by_username_parameter(
        self, client, fake, jq, announcement_factory, announcement_crud
    ):
        created_announcements = await announcement_factory.bulk_create(2)
        announcement_ids = created_announcements.get_field_values('id', str)
        announcement_id = announcement_ids.pop(0)
        username = fake.user_name()
        await announcement_crud.unsubscribe_user(announcement_id, username)

        response = await client.get('/v2/announcements/', params={'username': username})

        body = jq(response)
        received_announcement_ids = body('.result[].id').all()
        received_total = body('.total').first()

        assert received_announcement_ids == announcement_ids
        assert received_total == 1

    async def test_get_announcement_returns_announcement_by_id(self, client, announcement_factory):
        created_announcement = await announcement_factory.create()

        response = await client.get(f'/v2/announcements/{created_announcement.id}')

        assert response.status_code == 200

        received_announcement = response.json()

        assert received_announcement['id'] == str(created_announcement.id)

    async def test_create_announcement_creates_new_announcement(
        self, client, jq, announcement_factory, announcement_crud
    ):
        announcement = announcement_factory.generate()

        payload = announcement.to_payload()
        response = await client.post('/v2/announcements/', json=payload)

        assert response.status_code == 200

        body = jq(response)
        received_announcement_id = body('.id').first()
        received_announcement = await announcement_crud.retrieve_by_id(received_announcement_id)

        assert received_announcement.message == announcement.message

    async def test_create_announcement_creates_also_maintenance_notification(
        self, client, jq, announcement_factory, notification_crud
    ):
        announcement = announcement_factory.generate()

        payload = announcement.to_payload()
        response = await client.post('/v2/announcements/', json=payload)

        assert response.status_code == 200

        body = jq(response)
        received_announcement_id = body('.id').first()
        received_notification = await notification_crud.retrieve_by_announcement_id(received_announcement_id)

        assert received_notification.message == announcement.message

    @pytest.mark.parametrize('parameter', ['effective_date', 'duration_minutes', 'message'])
    async def test_update_announcement_updates_announcement_field_by_id(
        self, parameter, client, jq, announcement_factory, announcement_crud, db_session
    ):
        created_announcement = await announcement_factory.create()
        announcement = announcement_factory.generate()
        expected_parameter = getattr(announcement, parameter)

        value = expected_parameter
        if parameter == 'effective_date':
            value = value.isoformat()

        response = await client.patch(f'/v2/announcements/{created_announcement.id}', json={parameter: value})

        assert response.status_code == 200

        body = jq(response)
        received_announcement_id = body('.id').first()

        db_session.expire_all()
        received_announcement = await announcement_crud.retrieve_by_id(received_announcement_id)
        received_parameter = getattr(received_announcement, parameter)

        assert received_parameter == expected_parameter

    async def test_update_announcement_removes_unsubscriptions_from_it_for_all_users(
        self, client, fake, announcement_factory, announcement_crud
    ):
        created_announcement = await announcement_factory.create()
        await announcement_crud.unsubscribe_user(created_announcement.id, fake.user_name())

        response = await client.patch(
            f'/v2/announcements/{created_announcement.id}', json={'duration_minutes': fake.positive_int()}
        )

        assert response.status_code == 200

        unsubscriptions = await announcement_crud.list_unsubscriptions(created_announcement.id)

        assert unsubscriptions == []

    async def test_update_announcement_recreates_new_maintenance_notification(
        self, client, fake, announcement_factory, notification_crud
    ):
        created_announcement = await announcement_factory.create()
        created_notification = await notification_crud.create_from_announcement(created_announcement)
        message = fake.sentence()

        response = await client.patch(f'/v2/announcements/{created_announcement.id}', json={'message': message})

        assert response.status_code == 200

        received_notification = await notification_crud.retrieve_by_announcement_id(created_announcement.id)

        assert received_notification.message == message
        with pytest.raises(NotFound):
            await notification_crud.retrieve_by_id(created_notification.id)

    async def test_delete_announcement_removes_announcement_by_id(
        self, client, announcement_factory, announcement_crud
    ):
        created_announcement = await announcement_factory.create()

        response = await client.delete(f'/v2/announcements/{created_announcement.id}')

        assert response.status_code == 204

        with pytest.raises(NotFound):
            await announcement_crud.retrieve_by_id(created_announcement.id)

    async def test_delete_announcement_deletes_also_maintenance_notification(
        self, client, jq, announcement_factory, notification_crud
    ):
        created_announcement = await announcement_factory.create()
        created_notification = await notification_crud.create_from_announcement(created_announcement)

        response = await client.delete(f'/v2/announcements/{created_announcement.id}')

        assert response.status_code == 204

        with pytest.raises(NotFound):
            await notification_crud.retrieve_by_id(created_notification.id)

    async def test_unsubscribe_from_announcement_creates_unsubscription_for_specified_username(
        self, client, fake, announcement_factory, announcement_crud
    ):
        created_announcement = await announcement_factory.create()
        username = fake.user_name()

        payload = AnnouncementUnsubscriptionCreateSchema(username=username).to_payload()
        response = await client.post(f'/v2/announcements/{created_announcement.id}/unsubscribe', json=payload)

        assert response.status_code == 204

        unsubscriptions = await announcement_crud.list_unsubscriptions(created_announcement.id)

        assert len(unsubscriptions) == 1
        assert unsubscriptions[0].username == username
