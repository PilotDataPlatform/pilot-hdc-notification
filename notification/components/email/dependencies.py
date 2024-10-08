# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Depends

from notification.components.email.email_client import EmailClient
from notification.config import Settings
from notification.config import get_settings


def get_email_client(settings: Settings = Depends(get_settings)) -> EmailClient:
    """Return an instance of EmailClient as a dependency."""

    return EmailClient(
        settings.POSTFIX_URL,
        settings.POSTFIX_PORT,
        settings.SMTP_USER,
        settings.SMTP_PASS,
    )
