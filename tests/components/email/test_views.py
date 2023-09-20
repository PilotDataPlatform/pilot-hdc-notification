# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

import base64
import socket

import pytest


@pytest.fixture
def smtp_mocker(mocker):
    yield mocker.patch('smtplib.SMTP', autospec=True)


class TestEmailViews:
    async def test_post_correct(self, client, smtp_mocker):
        payload = {
            'sender': 'sender@test.com',
            'receiver': ['receiver@test.com'],
            'message': 'Test email contents',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 200
        assert smtp_mocker.call_count == 2
        assert smtp_mocker.return_value.login.call_count == 2
        assert smtp_mocker.return_value.sendmail.call_count == 1

    async def test_post_no_sender(self, client):
        payload = {
            'sender': None,
            'receiver': 'receiver@test.com',
            'message': 'test email',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 422
        assert 'none is not an allowed value' in response.text

    async def test_post_no_receiver(self, client):
        payload = {
            'sender': 'sender@test.com',
            'receiver': None,
            'message': 'test email',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 422
        assert 'none is not an allowed value' in response.text

    async def test_post_no_message(self, client):
        payload = {
            'sender': 'sender@test.com',
            'receiver': ['receiver@test.com'],
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 422
        assert 'message or template is required' in response.text

    async def test_html_email(self, client, smtp_mocker):
        html_msg = '''<!DOCTYPE html> \
                        <body>\
                        <h4>Dear member,</h4>\
                        </body>\
            </html>'''
        payload = {
            'sender': 'sender@test.com',
            'receiver': ['receiver@test.com'],
            'message': html_msg,
            'msg_type': 'html',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 200
        assert smtp_mocker.call_count == 2
        assert smtp_mocker.return_value.login.call_count == 2
        assert smtp_mocker.return_value.sendmail.call_count == 1

    async def test_wrong_message(self, client):
        payload = {
            'sender': 'sender@test.com',
            'receiver': ['receiver@test.com'],
            'message': 'test message',
            'msg_type': 'csv',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 422
        assert "unexpected value; permitted: 'html', 'plain'" in response.text

    async def test_multiple_receiver_list(self, client, smtp_mocker):
        payload = {
            'sender': 'sender@test.com',
            'receiver': ['receiver@test.com', 'receiver2@test.com'],
            'message': 'test email',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 200
        assert smtp_mocker.call_count == 2
        assert smtp_mocker.return_value.login.call_count == 2
        assert smtp_mocker.return_value.sendmail.call_count == 2

    async def test_list_receiver(self, client, smtp_mocker):
        payload = {
            'sender': 'sender@test.com',
            'receiver': ['receiver@test.com'],
            'message': 'test email',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 200
        assert smtp_mocker.call_count == 2
        assert smtp_mocker.return_value.login.call_count == 2
        assert smtp_mocker.return_value.sendmail.call_count == 1

    async def test_smtp_error(self, client, smtp_mocker):
        smtp_mocker.side_effect = socket.gaierror
        payload = {
            'sender': 'sender@test.com',
            'receiver': ['receiver@test.com'],
            'message': 'test email',
        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 500
        assert response.content is not None

    async def test_send_email_with_png_attachment(self, client, tmp_path, smtp_mocker):
        png_path = tmp_path / 'test1.png'
        png_path.write_bytes(b'')

        with open(png_path, 'rb') as img:
            payload = {
                'sender': 'sender@test.com',
                'receiver': ['receiver@test.com'],
                'message': 'test email',
                'subject': 'test email',
                'msg_type': 'plain',
                'attachments': [
                    {
                        'name': str(png_path),
                        'data': base64.b64encode(
                            img.read() + b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00IEND\xaeB`\x82'
                        ).decode('utf-8'),
                    }
                ],
            }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 200
        assert smtp_mocker.call_count == 2
        assert smtp_mocker.return_value.login.call_count == 2
        assert smtp_mocker.return_value.sendmail.call_count == 1

    async def test_send_email_with_multiple_attachments(self, client, tmp_path, smtp_mocker):
        pdf_path = tmp_path / 'test2.pdf'
        jpg_path = tmp_path / 'test3.jpg'
        jpeg_path = tmp_path / 'test4.jpeg'
        gif_path = tmp_path / 'test5.gif'
        for file_path in (pdf_path, jpg_path, jpeg_path, gif_path):
            file_path.write_bytes(b'')

        with open(pdf_path, 'rb') as img1:
            with open(jpg_path, 'rb') as img2:
                with open(jpeg_path, 'rb') as img3:
                    with open(gif_path, 'rb') as img4:
                        payload = {
                            'sender': 'sender@test.com',
                            'receiver': ['receiver@test.com'],
                            'message': 'test email',
                            'subject': 'test email',
                            'msg_type': 'plain',
                            'attachments': [
                                {
                                    'name': str(pdf_path),
                                    'data': base64.b64encode(
                                        img1.read() + b'\x89PDF\r\n\x1a\n\x00\rIHDR\x00\x00IEND\xaeB`\x82'
                                    ).decode('utf-8'),
                                },
                                {
                                    'name': str(jpg_path),
                                    'data': base64.b64encode(
                                        img2.read() + b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x00\x00?\xff\xd9'
                                    ).decode('utf-8'),
                                },
                                {
                                    'name': str(jpeg_path),
                                    'data': base64.b64encode(
                                        img3.read() + b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x00\x00?\xff\xd9'
                                    ).decode('utf-8'),
                                },
                                {
                                    'name': str(gif_path),
                                    'data': base64.b64encode(
                                        img4.read() + b'GIF89a,\x01,\x01\xf7\x13\x00\xff\x95\x99]f\x85d\x00;'
                                    ).decode('utf-8'),
                                },
                            ],
                        }
        response = await client.post('/v1/email/', json=payload)
        assert response.status_code == 200
        assert smtp_mocker.call_count == 2
        assert smtp_mocker.return_value.login.call_count == 2
        assert smtp_mocker.return_value.sendmail.call_count == 1

    async def test_send_email_with_unsupported_attachment(self, client, tmp_path, smtp_mocker):
        xml_path = tmp_path / 'invalid.xml'
        xml_path.write_bytes(b'')

        with open(xml_path, 'rb') as img:
            payload = {
                'sender': 'sender@test.com',
                'receiver': ['receiver@test.com'],
                'message': 'test email',
                'subject': 'test email',
                'msg_type': 'plain',
                'attachments': [
                    {
                        'name': 'invalid.xml',
                        'data': base64.b64encode(img.read()).decode('utf-8'),
                    }
                ],
            }
        response = await client.post('/v1/email/', json=payload)
        assert smtp_mocker.call_count == 0
        assert smtp_mocker.return_value.login.call_count == 0
        assert response.status_code == 422

    async def test_send_email_with_large_attachment(self, client, tmp_path, settings, smtp_mocker):
        large_file_path = tmp_path / 'invalid_large.pdf'
        large_file_path.write_bytes(b'\0' * (settings.EMAIL_ATTACHMENT_MAX_SIZE_BYTES + 1))

        with open(large_file_path, 'rb') as img:
            payload = {
                'sender': 'sender@test.com',
                'receiver': ['receiver@test.com'],
                'message': 'test email',
                'subject': 'test email',
                'msg_type': 'plain',
                'attachments': [
                    {
                        'name': 'invalid_large.pdf',
                        'data': base64.b64encode(img.read()).decode('utf-8'),
                    }
                ],
            }
        response = await client.post('/v1/email/', json=payload)
        assert smtp_mocker.call_count == 0
        assert smtp_mocker.return_value.login.call_count == 0
        assert response.status_code == 422
