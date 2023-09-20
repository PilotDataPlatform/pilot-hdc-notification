# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from __future__ import annotations as _annotations

from typing import Any
from typing import TypeVar

from pydantic import BaseModel

Model = TypeVar('Model', bound=BaseModel)


class ModelList(list):
    """Store a list of models of the same type."""

    def __getitem__(self, item: Any) -> Model | ModelList:
        """Return one item or a slice of the same class."""

        result = super().__getitem__(item)

        if isinstance(item, slice):
            return self.__class__(result)

        return result

    def map_by_field(self, field: str, key_type: type | None = None) -> dict[Any, Any]:
        """Create map using field argument as key with optional type casting."""

        results = {}

        for source in self:
            key = getattr(source, field)

            if key_type is not None:
                key = key_type(key)

            results[key] = source

        return results

    def get_field_values(self, field: str, value_type: type | None = None) -> list[Any]:
        """Return list with values each model has in field attribute with optional type casting."""

        results = []

        for source in self:
            value = getattr(source, field)

            if value_type is not None:
                value = value_type(value)

            results.append(value)

        return results
