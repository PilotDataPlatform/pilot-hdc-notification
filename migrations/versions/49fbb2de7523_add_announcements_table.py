# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

"""Add announcements table.

Revision ID: 49fbb2de7523
Revises: acfc65939c91
Create Date: 2022-01-21 12:01:11.749704
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '49fbb2de7523'
down_revision = 'acfc65939c91'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'announcement',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_code', sa.String(), nullable=True),
        sa.Column('content', sa.String(), nullable=True),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('publisher', sa.String(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('project_code', 'version', name='project_code_version'),
    )


def downgrade():
    op.drop_table('announcement')
