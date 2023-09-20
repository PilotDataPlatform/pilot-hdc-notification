# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

"""Delete maintenance notifications.

Revision ID: 0011
Revises: 0010
Create Date: 2022-12-14 14:48:42.909111
"""

from alembic import op

revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = '0010'


def upgrade():
    op.execute('DELETE FROM notifications WHERE "type" = \'maintenance\';')


def downgrade():
    pass
