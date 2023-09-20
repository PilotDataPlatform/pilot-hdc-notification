# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

"""Add project_code column to Notifications table.

Revision ID: c7aab7287203
Revises: 64a329367547
Create Date: 2022-11-03 16:46:24.671867
"""
import sqlalchemy as sa
from alembic import op
from alembic.operations.schemaobj import SchemaObjects
from alembic.runtime.migration import MigrationContext
from sqlalchemy import func
from sqlalchemy import update
from sqlalchemy.dialects import postgresql
from sqlalchemy.future import select

revision = '0006'
down_revision = '64a329367547'
branch_labels = None
depends_on = None


def load_notifications_table(context: MigrationContext) -> sa.Table:
    schema = SchemaObjects(context)
    return schema.table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_code', sa.VARCHAR(length=32), nullable=True),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )


def upgrade():
    op.add_column('notifications', sa.Column('project_code', sa.VARCHAR(length=32), nullable=True))
    op.create_index(op.f('ix_notification_notifications_project_code'), 'notifications', ['project_code'], unique=False)

    context = op.get_context()
    notification = load_notifications_table(context)

    cursor = context.connection.execute(select(notification.c.id, notification.c.data['project_code']))
    for row_id, project_code in cursor:
        context.connection.execute(
            update(notification)
            .where(notification.c.id == row_id)
            .values(
                {
                    notification.c.project_code: project_code,
                    notification.c.data: notification.c.data - 'project_code',
                }
            )
        )


def downgrade():
    context = op.get_context()
    notification = load_notifications_table(context)

    cursor = context.connection.execute(select(notification.c.id, notification.c.project_code))
    for row_id, project_code in cursor:
        context.connection.execute(
            update(notification)
            .where(notification.c.id == row_id)
            .values(
                {
                    notification.c.data: func.jsonb_insert(notification.c.data, '{project_code}', f'"{project_code}"'),
                }
            )
        )

    op.drop_index(op.f('ix_notification_notifications_project_code'), table_name='notifications')
    op.drop_column('notifications', 'project_code')
