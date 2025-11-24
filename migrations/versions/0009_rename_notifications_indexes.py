# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.
"""Rename notifications indexes.

Revision ID: 0009
Revises: 0008
Create Date: 2022-12-07 18:23:40.031288
"""

from alembic import op

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = '0008'


def upgrade():
    for column in {'created_at', 'project_code', 'recipient_username', 'type'}:
        op.execute(f'ALTER INDEX IF EXISTS ix_notification_notifications_{column} RENAME TO ix_notifications_{column};')


def downgrade():
    for column in {'created_at', 'project_code', 'recipient_username', 'type'}:
        op.execute(f'ALTER INDEX IF EXISTS ix_notifications_{column} RENAME TO ix_notification_notifications_{column};')
