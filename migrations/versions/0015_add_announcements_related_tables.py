# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

"""Add announcements related tables.

Revision ID: 0015
Revises: 0014
Create Date: 2023-02-24 17:30:31.010420
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = '0014'


def tables_exist(tables: set[str]) -> bool:
    context = op.get_context()
    available_tables = inspect(context.bind).get_table_names()
    return tables.issubset(set(available_tables))


def upgrade():
    if tables_exist({'announcements', 'announcement_unsubscriptions'}):
        return

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
