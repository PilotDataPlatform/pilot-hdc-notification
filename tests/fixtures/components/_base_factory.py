# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from faker import Faker
from sqlalchemy import text

from notification.components.crud import CRUD


class BaseFactory:
    """Base class for creating testing purpose entries."""

    crud: CRUD
    fake: Faker

    def __init__(self, crud: CRUD, fake: Faker) -> None:
        self.crud = crud
        self.fake = fake

    async def truncate_table(self) -> None:
        """Remove all rows from a table."""

        statement = text(f'TRUNCATE TABLE {self.crud.model.__table__} CASCADE')
        await self.crud.execute(statement)
