# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from base64 import b64encode

import pytest

from notification.components.email.schemas import SendEmailAttachmentSchema
from notification.components.email.schemas import SendEmailSchema


class TestSendEmailAttachmentSchema:
    def test_data_field_decodes_base64_value(self, fake):
        value = fake.pystr().encode()
        attachment = SendEmailAttachmentSchema(name=fake.file_name(extension='jpg'), data=b64encode(value).decode())

        assert attachment.data == value

    def test_data_field_decodes_base64_value_with_data_prefix(self, fake):
        value = fake.pystr().encode()
        attachment = SendEmailAttachmentSchema(
            name=fake.file_name(extension='png'), data=(b'data:image/png;base64,' + b64encode(value)).decode()
        )

        assert attachment.data == value

    def test_data_field_raises_value_error_for_invalid_value(self, fake):
        with pytest.raises(ValueError, match='invalid base64 string'):
            SendEmailAttachmentSchema(name=fake.pystr(), data='invalid')

    def test_data_field_raises_value_error_when_value_exceeds_max_size(self, fake, settings):
        value = fake.binary(settings.EMAIL_ATTACHMENT_MAX_SIZE_BYTES + 1)

        with pytest.raises(ValueError, match='attachment to large'):
            SendEmailAttachmentSchema(name=fake.file_name(extension='jpg'), data=b64encode(value).decode())

    def test_name_field_raises_value_error_for_not_allowed_extensions(self):
        with pytest.raises(ValueError, match='file type is not allowed'):
            SendEmailAttachmentSchema(name='file.raw', data='')

    def test_is_image_returns_true_when_name_extension_listed_in_image_extensions(self):
        attachment = SendEmailAttachmentSchema(name='image.jpg', data='')

        assert attachment.is_image is True

    def test_is_image_returns_false_when_name_extension_is_not_listed_in_image_extensions(self):
        attachment = SendEmailAttachmentSchema(name='file.pdf', data='')

        assert attachment.is_image is False


class TestSendEmailSchema:
    def test_check_parameters_raises_value_error_when_both_message_and_template_are_set(self, fake):
        with pytest.raises(ValueError, match='please set message or template, not both'):
            SendEmailSchema(sender=fake.email(), receiver=[], message=fake.pystr(), template=fake.pystr())

    def test_check_parameters_raises_value_error_when_both_message_and_template_are_not_set(self, fake):
        with pytest.raises(ValueError, match='message or template is required'):
            SendEmailSchema(sender=fake.email(), receiver=[])

    def test_check_parameters_raises_value_error_when_wrong_template_is_specified(self, fake):
        with pytest.raises(ValueError, match='template not found'):
            SendEmailSchema(sender=fake.email(), receiver=[], template=fake.pystr())

    def test_check_parameters_overrides_message_field_with_html_markup_when_template_is_specified(self, fake):
        send_email = SendEmailSchema(
            sender=fake.email(),
            receiver=[],
            message='',
            template='auth/reset_password.html',
            template_kwargs={'hours': 2},
        )

        assert send_email.message.startswith('<!DOCTYPE html>') is True

    def test_msg_type_field_raises_value_error_for_invalid_value(self, fake):
        with pytest.raises(ValueError, match="unexpected value; permitted: 'html', 'plain'"):
            SendEmailSchema(sender=fake.email(), receiver=[], message=fake.pystr(), msg_type=fake.pystr())
