# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from base64 import b64decode
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Literal

from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from jinja2.exceptions import TemplateNotFound
from pydantic import EmailStr
from pydantic import root_validator
from pydantic import validator

from notification.components.schemas import BaseSchema
from notification.config import get_settings


class EAPIResponseCode(Enum):
    success = 200
    internal_error = 500
    bad_request = 400
    not_found = 404
    forbidden = 403
    unauthorized = 401
    conflict = 409
    to_large = 413


class APIResponse(BaseSchema):
    code: EAPIResponseCode = EAPIResponseCode.success
    error_msg: str = ''
    page: int = 0
    total: int = 1
    num_of_pages: int = 1
    result = []

    def json_response(self) -> JSONResponse:
        data = self.dict()
        data['code'] = self.code.value
        return JSONResponse(status_code=self.code.value, content=data)

    def set_error_msg(self, error_msg):
        self.error_msg = error_msg

    def set_code(self, code):
        self.code = code


class SendEmailAttachmentSchema(BaseSchema):
    """Email attachment schema."""

    name: str
    data: str

    @validator('data')
    def decode_data(cls, value: str) -> bytes:
        if ',' in value:
            _, value = value.split(',', 1)

        try:
            data = b64decode(value)
        except Exception:
            raise ValueError('invalid base64 string')

        if len(data) > get_settings().EMAIL_ATTACHMENT_MAX_SIZE_BYTES:
            raise ValueError('attachment to large')

        return data

    @validator('name')
    def is_allowed_file(cls, value: str) -> str:
        extension = Path(value).suffix.lstrip('.')
        if extension in get_settings().ALLOWED_EXTENSIONS:
            return value

        raise ValueError('file type is not allowed')

    @property
    def is_image(self) -> bool:
        extension = Path(self.name).suffix.lstrip('.')
        return extension in get_settings().IMAGE_EXTENSIONS

    def to_mime_attachment(self) -> MIMEImage | MIMEApplication:
        if self.is_image:
            attach = MIMEImage(self.data)
            attach.add_header('Content-Disposition', 'attachment', filename=self.name)
            return attach

        attach = MIMEApplication(self.data, _subtype='pdf', filename=self.name)
        attach.add_header('Content-Disposition', 'attachment', filename=self.name)
        return attach


class SendEmailSchema(BaseSchema):
    """Schema used for email sending request."""

    sender: EmailStr
    receiver: list[EmailStr]
    subject: str = ''
    message: str = ''
    template: str = ''
    template_kwargs: dict[str, Any] = {}
    msg_type: Literal['html', 'plain'] = 'plain'
    attachments: list[SendEmailAttachmentSchema] = []

    @root_validator
    def check_parameters(cls, values: dict[str, Any]) -> dict[str, Any]:
        message, template = values.get('message'), values.get('template')

        if message and template:
            raise ValueError('please set message or template, not both')

        if not message and not template:
            raise ValueError('message or template is required')

        templates_dir = Path(__file__).parent / 'templates'
        templates = Jinja2Templates(directory=templates_dir)

        if template:
            template_kwargs = values.get('template_kwargs')
            try:
                template = templates.get_template(template)
                values['message'] = template.render(template_kwargs)
            except TemplateNotFound:
                raise ValueError('template not found')

        return values

    def to_mime_text(self) -> MIMEText:
        if self.msg_type == 'plain':
            return MIMEText(self.message, 'plain', 'utf-8')

        return MIMEText(self.message, 'html', 'utf-8')
