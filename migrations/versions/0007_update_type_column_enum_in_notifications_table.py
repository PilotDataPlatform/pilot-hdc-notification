# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.
"""Update type column enum in Notifications table.

Revision ID: 0007
Revises: 0006
Create Date: 2022-11-16 22:21:51.783669
"""

from alembic import op

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = '0006'


def upgrade():
    op.execute('ALTER TYPE "notification_type" RENAME VALUE \'platform\' TO \'maintenance\';')


def downgrade():
    op.execute('ALTER TYPE "notification_type" RENAME VALUE \'maintenance\' TO \'platform\';')
