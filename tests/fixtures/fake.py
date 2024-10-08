# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from datetime import datetime
from datetime import timezone

import faker
import pytest


class Faker(faker.Faker):
    def past_datetime_utc(self) -> datetime:
        return self.past_datetime(tzinfo=timezone.utc)

    def positive_int(self) -> int:
        return self.pyint(min_value=1)


@pytest.fixture(scope='session')
def fake() -> Faker:
    yield Faker()
