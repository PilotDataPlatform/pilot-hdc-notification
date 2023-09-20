# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from http import HTTPStatus

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from notification.components.notification.crud import NotificationCRUD
from notification.components.notification.dependencies import get_notification_crud
from notification.components.notification.parameters import NotificationFilterParameters
from notification.components.notification.parameters import NotificationSortByFields
from notification.components.notification.parameters import UserNotificationFilterParameters
from notification.components.notification.schemas import NotificationListResponseSchema
from notification.components.notification.schemas import NotificationsCreateSchema
from notification.components.parameters import PageParameters
from notification.components.parameters import SortParameters

router = APIRouter(prefix='/notifications', tags=['Notifications'])


@router.get(
    '/', summary='List all notifications.', response_model=NotificationListResponseSchema, status_code=HTTPStatus.OK
)
async def list_notifications(
    filter_parameters: NotificationFilterParameters = Depends(),
    sort_parameters: SortParameters.with_sort_by_fields(NotificationSortByFields) = Depends(),
    page_parameters: PageParameters = Depends(),
    notification_crud: NotificationCRUD = Depends(get_notification_crud),
) -> NotificationListResponseSchema:
    """List notifications."""

    filtering = filter_parameters.to_filtering()
    sorting = sort_parameters.to_sorting()
    pagination = page_parameters.to_pagination()

    page = await notification_crud.paginate(pagination, sorting, filtering)

    response = NotificationListResponseSchema.from_page(page)

    return response


@router.get(
    '/user',
    summary='List user notifications.',
    response_model=NotificationListResponseSchema,
    status_code=HTTPStatus.OK,
)
async def list_user_notifications(
    filter_parameters: UserNotificationFilterParameters = Depends(),
    sort_parameters: SortParameters.with_sort_by_fields(NotificationSortByFields) = Depends(),
    page_parameters: PageParameters = Depends(),
    notification_crud: NotificationCRUD = Depends(get_notification_crud),
) -> NotificationListResponseSchema:
    """List user notifications."""

    filtering = filter_parameters.to_filtering()
    sorting = sort_parameters.to_sorting()
    pagination = page_parameters.to_pagination()

    page = await notification_crud.paginate(pagination, sorting, filtering)

    response = NotificationListResponseSchema.from_page(page)

    return response


@router.post('/', summary='Create new notification(s).', status_code=HTTPStatus.NO_CONTENT)
async def create_notification(
    body: NotificationsCreateSchema | list[NotificationsCreateSchema],
    notification_crud: NotificationCRUD = Depends(get_notification_crud),
) -> Response:
    """Create one or multiple notifications."""

    if not isinstance(body, list):
        body = [body]

    for entry in body:
        await notification_crud.create(entry)

    await notification_crud.commit()

    return Response(status_code=HTTPStatus.NO_CONTENT)
