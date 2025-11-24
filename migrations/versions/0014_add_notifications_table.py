# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.
"""Add notifications table.

Revision ID: 0014
Revises: 0013
Create Date: 2023-02-24 15:52:57.581279
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = '0013'


def tables_exist(tables: set[str]) -> bool:
    context = op.get_context()
    available_tables = inspect(context.bind).get_table_names()
    return tables.issubset(set(available_tables))


def upgrade():
    if tables_exist({'notifications'}):
        return

    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'type',
            postgresql.ENUM(
                'pipeline',
                'copy-request',
                'role-change',
                'project',
                'maintenance',
                name='notification_type',
            ),
            nullable=False,
        ),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('recipient_username', sa.VARCHAR(length=256), nullable=True),
        sa.Column('project_code', sa.VARCHAR(length=32), nullable=True),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_notifications_project_code'), 'notifications', ['project_code'], unique=False)
    op.create_index(op.f('ix_notifications_recipient_username'), 'notifications', ['recipient_username'], unique=False)
    op.create_index(op.f('ix_notifications_type'), 'notifications', ['type'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notifications_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_recipient_username'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_project_code'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_table('notifications')
    op.execute('DROP TYPE "notification_type";')
