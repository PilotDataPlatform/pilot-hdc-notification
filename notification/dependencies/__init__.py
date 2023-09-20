# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from notification.dependencies.db import get_db_engine
from notification.dependencies.db import get_db_session

__all__ = [
    'get_db_engine',
    'get_db_session',
]
