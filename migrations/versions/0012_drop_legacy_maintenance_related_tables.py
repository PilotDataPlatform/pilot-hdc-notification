# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

"""Drop legacy maintenance related tables.

Revision ID: 0012
Revises: 0011
Create Date: 2022-12-14 14:48:42.909111
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = '0011'


def upgrade():
    op.drop_table('unsubscribed_notifications')
    op.drop_table('system_maintenance')


def downgrade():
    op.create_table(
        'system_maintenance',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('message', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('maintenance_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('duration', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('duration_unit', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='system_maintenance_pkey'),
    )
    op.create_table(
        'unsubscribed_notifications',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('notification_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name='unsubscribed_notifications_pkey'),
    )
