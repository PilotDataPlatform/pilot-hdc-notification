# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from pydantic import BaseModel
from sqlalchemy.sql import Select

from notification.components.db_model import DBModel


class Filtering(BaseModel):
    """Base filtering control parameters."""

    def __bool__(self) -> bool:
        """Filtering considered valid when at least one attribute has a value."""

        values = self.dict()

        for name in self.__fields__.keys():
            if values[name] is not None:
                return True

        return False

    def apply(self, statement: Select, model: type[DBModel]) -> Select:
        """Return statement with applied filtering."""

        raise NotImplementedError
