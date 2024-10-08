# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

pytest_plugins = [
    'tests.fixtures.components.announcement',
    'tests.fixtures.components.notification',
    'tests.fixtures.app',
    'tests.fixtures.db',
    'tests.fixtures.fake',
    'tests.fixtures.jq',
]
