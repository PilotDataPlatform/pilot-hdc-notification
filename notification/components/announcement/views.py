# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from contextlib import suppress
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import Response

from notification.components.announcement.crud import AnnouncementCRUD
from notification.components.announcement.dependencies import get_announcement_crud
from notification.components.announcement.parameters import AnnouncementFilterParameters
from notification.components.announcement.parameters import AnnouncementSortByFields
from notification.components.announcement.schemas import AnnouncementCreateSchema
from notification.components.announcement.schemas import AnnouncementListResponseSchema
from notification.components.announcement.schemas import AnnouncementResponseSchema
from notification.components.announcement.schemas import AnnouncementUnsubscriptionCreateSchema
from notification.components.announcement.schemas import AnnouncementUpdateSchema
from notification.components.exceptions import NotFound
from notification.components.notification.crud import NotificationCRUD
from notification.components.notification.dependencies import get_notification_crud
from notification.components.parameters import PageParameters
from notification.components.parameters import SortParameters

router = APIRouter(prefix='/announcements', tags=['Announcements'])


@router.get('/', summary='List all announcements.', response_model=AnnouncementListResponseSchema)
async def list_announcements(
    filter_parameters: AnnouncementFilterParameters = Depends(),
    sort_parameters: SortParameters.with_sort_by_fields(AnnouncementSortByFields) = Depends(),
    page_parameters: PageParameters = Depends(),
    announcement_crud: AnnouncementCRUD = Depends(get_announcement_crud),
) -> AnnouncementListResponseSchema:
    """List all announcements."""

    filtering = filter_parameters.to_filtering()
    sorting = sort_parameters.to_sorting()
    pagination = page_parameters.to_pagination()
    page = await announcement_crud.paginate(pagination, sorting, filtering)

    response = AnnouncementListResponseSchema.from_page(page)

    return response


@router.get('/{announcement_id}', summary='Get announcement by id.', response_model=AnnouncementResponseSchema)
async def get_announcement(
    announcement_id: UUID, announcement_crud: AnnouncementCRUD = Depends(get_announcement_crud)
) -> AnnouncementResponseSchema:
    """Get announcement by id."""

    announcement = await announcement_crud.retrieve_by_id(announcement_id)

    return announcement


@router.post('/', summary='Create new announcement.', response_model=AnnouncementResponseSchema)
async def create_announcement(
    body: AnnouncementCreateSchema,
    announcement_crud: AnnouncementCRUD = Depends(get_announcement_crud),
    notification_crud: NotificationCRUD = Depends(get_notification_crud),
) -> AnnouncementResponseSchema:
    """Create new announcement together with maintenance notification."""

    announcement = await announcement_crud.create(body)
    await notification_crud.create_from_announcement(announcement)

    await announcement_crud.commit()

    return announcement


@router.patch('/{announcement_id}', summary='Update announcement.', response_model=AnnouncementResponseSchema)
async def update_announcement(
    announcement_id: UUID,
    body: AnnouncementUpdateSchema,
    announcement_crud: AnnouncementCRUD = Depends(get_announcement_crud),
    notification_crud: NotificationCRUD = Depends(get_notification_crud),
) -> AnnouncementResponseSchema:
    """Update announcement and recreate related maintenance notification."""

    announcement = await announcement_crud.update(announcement_id, body)
    with suppress(NotFound):
        await announcement_crud.subscribe_all_users(announcement.id)
    with suppress(NotFound):
        await notification_crud.delete_by_announcement_id(announcement.id)
    await notification_crud.create_from_announcement(announcement)

    await announcement_crud.commit()

    return announcement


@router.delete('/{announcement_id}', summary='Delete announcement.')
async def delete_announcement(
    announcement_id: UUID,
    announcement_crud: AnnouncementCRUD = Depends(get_announcement_crud),
    notification_crud: NotificationCRUD = Depends(get_notification_crud),
) -> Response:
    """Delete announcement together with related maintenance notification."""

    await announcement_crud.delete(announcement_id)
    with suppress(NotFound):
        await notification_crud.delete_by_announcement_id(announcement_id)

    await announcement_crud.commit()

    return Response(status_code=204)


@router.post('/{announcement_id}/unsubscribe', summary='Unsubscribe user from announcement.')
async def unsubscribe_from_announcement(
    announcement_id: UUID,
    body: AnnouncementUnsubscriptionCreateSchema,
    announcement_crud: AnnouncementCRUD = Depends(get_announcement_crud),
) -> Response:
    """Unsubscribe user from announcement."""

    await announcement_crud.unsubscribe_user(announcement_id, body.username)

    await announcement_crud.commit()

    return Response(status_code=204)
