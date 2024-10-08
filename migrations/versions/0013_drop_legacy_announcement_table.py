# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

"""Drop legacy announcement table.

Revision ID: 0013
Revises: 0012
Create Date: 2022-12-14 14:13:00.459463
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = '0012'


def upgrade():
    op.drop_table('announcement')


def downgrade():
    op.create_table(
        'announcement',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('project_code', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('version', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('publisher', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='announcement_pkey'),
        sa.UniqueConstraint('project_code', 'version', name='project_code_version'),
    )
