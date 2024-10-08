# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

"""Add Notifications table.

Revision ID: 64a329367547
Revises: e6fcf3ec5303
Create Date: 2022-09-26 17:25:22.345194
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '64a329367547'
down_revision = 'e6fcf3ec5303'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'type',
            postgresql.ENUM('pipeline', 'copy-request', 'role-change', 'project', 'platform', name='notification_type'),
            nullable=False,
        ),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('recipient_username', sa.VARCHAR(length=256), nullable=True),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notification_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    op.create_index(
        op.f('ix_notification_notifications_recipient_username'), 'notifications', ['recipient_username'], unique=False
    )
    op.create_index(op.f('ix_notification_notifications_type'), 'notifications', ['type'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notification_notifications_type'), table_name='notifications')
    op.drop_index(op.f('ix_notification_notifications_recipient_username'), table_name='notifications')
    op.drop_index(op.f('ix_notification_notifications_created_at'), table_name='notifications')
    op.drop_table('notifications')
    op.execute('DROP TYPE "notification_type";')
