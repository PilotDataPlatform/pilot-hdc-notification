# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from common import LoggerFactory

from notification.components.email.schemas import APIResponse
from notification.components.email.schemas import EAPIResponseCode
from notification.config import get_settings

settings = get_settings()
_logger = LoggerFactory(
    __name__,
    level_default=settings.LOG_LEVEL_DEFAULT,
    level_file=settings.LOG_LEVEL_FILE,
    level_stdout=settings.LOG_LEVEL_STDOUT,
    level_stderr=settings.LOG_LEVEL_STDERR,
).get_logger()


class EmailClient:
    """Create content of email and send using SMTP server."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send_emails(self, receivers, sender, subject, text, msg_type, attachments):
        try:
            client = smtplib.SMTP(self.host, self.port)
            if self.username and self.password:
                client.login(self.username, self.password)
            _logger.info('email server connection established')
        except smtplib.socket.gaierror as e:
            _logger.exception(f'Error connecting with Mail host, {e}')
            api_response = APIResponse()
            api_response.result = str(e)
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()

        for to in receivers:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = to
            msg['Subject'] = Header(subject, 'utf-8')
            for attachment in attachments:
                msg.attach(attachment.to_mime_attachment())

            if msg_type == 'plain':
                msg.attach(MIMEText(text, 'plain', 'utf-8'))
            else:
                msg.attach(MIMEText(text, 'html', 'utf-8'))

            try:
                _logger.info(f"\nto: {to}\nfrom: {sender}\nsubject: {msg['Subject']}")
                client.sendmail(sender, to, msg.as_string())
            except Exception as e:
                _logger.exception(f'Error when sending email to {to}, {e}')
                api_response = APIResponse()
                api_response.result = str(e)
                api_response.code = EAPIResponseCode.internal_error
                return api_response.json_response()
        client.quit()
