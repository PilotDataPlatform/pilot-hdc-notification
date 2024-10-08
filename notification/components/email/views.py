# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import smtplib

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi.responses import JSONResponse

from notification.components.email.dependencies import get_email_client
from notification.components.email.email_client import EmailClient
from notification.components.email.schemas import APIResponse
from notification.components.email.schemas import EAPIResponseCode
from notification.components.email.schemas import SendEmailSchema
from notification.config import ConfigClass
from notification.logger import logger

router = APIRouter(prefix='/email', tags=['Email'])


@router.post('/', response_model=APIResponse, summary='Send emails')
async def send_emails(
    data: SendEmailSchema,
    background_tasks: BackgroundTasks,
    email_client: EmailClient = Depends(get_email_client),
) -> JSONResponse:
    """Compose and send emails based on templates."""

    api_response = APIResponse()
    text = data.message

    try:
        client = smtplib.SMTP(ConfigClass.POSTFIX_URL, ConfigClass.POSTFIX_PORT)
        if ConfigClass.SMTP_USER and ConfigClass.SMTP_PASS:
            client.login(ConfigClass.SMTP_USER, ConfigClass.SMTP_PASS)
        logger.info('email server connection established')
    except smtplib.socket.gaierror as e:
        api_response.result = str(e)
        api_response.code = EAPIResponseCode.internal_error
        return api_response.json_response()
    client.quit()

    background_tasks.add_task(
        email_client.send_emails, data.receiver, data.sender, data.subject, text, data.msg_type, data.attachments
    )
    logger.info(f'Email sent successfully to {data.receiver}')
    api_response.result = 'Email sent successfully. '
    return api_response.json_response()
