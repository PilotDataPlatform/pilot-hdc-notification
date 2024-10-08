# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from typing import Annotated

import pytest
from pydantic import BaseModel

from notification.components.schemas import BaseSchema
from notification.components.schemas import ParentOptionalFields


class TestParentOptionalFields:
    def test_usage_as_metaclass_makes_class_fields_optional(self):
        class CustomModel(BaseModel):
            field: int

        class InheritedCustomModel(CustomModel, metaclass=ParentOptionalFields):
            pass

        instance = InheritedCustomModel()
        assert instance.field is None

    def test_usage_as_metaclass_makes_optional_only_inherited_fields(self):
        class CustomModel(BaseModel):
            field1: int

        class InheritedCustomModel(CustomModel, metaclass=ParentOptionalFields):
            field2: int

        with pytest.raises(ValueError, match='field required'):
            InheritedCustomModel(field1=None)

    def test_usage_as_metaclass_does_not_change_field_type(self):
        class CustomModel(BaseModel):
            field: int

        class InheritedCustomModel(CustomModel, metaclass=ParentOptionalFields):
            pass

        with pytest.raises(ValueError, match='value is not a valid integer'):
            InheritedCustomModel(field='not_int')


class TestBaseSchema:
    def test_get_fields_annotated_with_returns_fields_annotated_with_specified_annotation_type(self):
        class CustomType(BaseModel):
            pass

        class CustomSchema(BaseSchema):
            field1: str
            field2: Annotated[str, CustomType]
            field3: CustomType

        received_fields = CustomSchema.get_fields_annotated_with(CustomType)

        assert received_fields == ['field2']
