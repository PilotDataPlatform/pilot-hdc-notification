# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

"""Alter all schemas to public.

Revision ID: 0008
Revises: 0007
Create Date: 2022-12-02 10:35:15.777679
"""

from alembic import op

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = '0007'


def upgrade():
    op.execute('ALTER TABLE IF EXISTS announcements.announcement SET SCHEMA public;')
    op.execute('ALTER TABLE IF EXISTS notifications.system_maintenance SET SCHEMA public;')
    op.execute('ALTER TABLE IF EXISTS notifications.unsubscribed_notifications SET SCHEMA public;')
    op.execute('ALTER TABLE IF EXISTS notification.notifications SET SCHEMA public;')

    op.execute('DROP SCHEMA IF EXISTS announcements;')
    op.execute('DROP SCHEMA IF EXISTS notifications;')
    op.execute('DROP SCHEMA IF EXISTS notification;')


def downgrade():
    op.execute('CREATE SCHEMA IF NOT EXISTS announcements;')
    op.execute('CREATE SCHEMA IF NOT EXISTS notifications;')
    op.execute('CREATE SCHEMA IF NOT EXISTS notification;')

    op.execute('ALTER TABLE IF EXISTS public.announcement SET SCHEMA announcements;')
    op.execute('ALTER TABLE IF EXISTS public.system_maintenance SET SCHEMA notifications;')
    op.execute('ALTER TABLE IF EXISTS public.unsubscribed_notifications SET SCHEMA notifications;')
    op.execute('ALTER TABLE IF EXISTS public.notifications SET SCHEMA notification;')
