# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

"""Add system_maintenance table.

Revision ID: f7b7903f78c4
Revises:
Create Date: 2022-01-21 11:53:38.076126
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f7b7903f78c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'system_maintenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('maintenance_date', sa.DateTime(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('duration_unit', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )


def downgrade():
    op.drop_table('system_maintenance')
