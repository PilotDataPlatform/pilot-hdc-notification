# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

"""Add tables related to announcements.

Revision ID: 0010
Revises: 0009
Create Date: 2022-12-08 16:00:09.640892
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = '0009'


def upgrade():
    op.create_table(
        'announcements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('effective_date', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('message', sa.VARCHAR(length=512), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_announcements_created_at'), 'announcements', ['created_at'], unique=False)
    op.create_index(op.f('ix_announcements_effective_date'), 'announcements', ['effective_date'], unique=False)
    op.create_table(
        'announcement_unsubscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('announcement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.VARCHAR(length=256), nullable=False),
        sa.ForeignKeyConstraint(['announcement_id'], ['announcements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('announcement_id', 'username', name='announcement_id_username_unique'),
    )


def downgrade():
    op.drop_table('announcement_unsubscriptions')
    op.drop_index(op.f('ix_announcements_effective_date'), table_name='announcements')
    op.drop_index(op.f('ix_announcements_created_at'), table_name='announcements')
    op.drop_table('announcements')
