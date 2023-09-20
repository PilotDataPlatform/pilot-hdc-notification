# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from pydantic import BaseModel

from notification.components.models import ModelList


class TestModelList:
    def test_map_by_field_returns_map_based_on_field_argument_as_key(self, fake):
        class Model(BaseModel):
            id: int

        model_1 = Model(id=fake.pyint())
        model_2 = Model(id=fake.pyint())

        models = ModelList([model_1, model_2])

        expected_map = {
            str(model_1.id): model_1,
            str(model_2.id): model_2,
        }

        assert models.map_by_field('id', str) == expected_map

    def test_get_field_values_returns_list_with_values_each_model_has_in_field_attribute(self, fake):
        class Model(BaseModel):
            key: str

        model_1 = Model(key=fake.word())
        model_2 = Model(key=fake.word())

        models = ModelList([model_1, model_2])

        expected_list = [model_1.key, model_2.key]

        assert models.get_field_values('key', str) == expected_list

    def test__getitem__returns_a_slice_of_the_same_class(self):
        model_1 = BaseModel()
        model_2 = BaseModel()

        models = ModelList([model_1, model_2])

        expected_list = ModelList([model_1])

        received_list = models[:-1]

        assert isinstance(received_list, ModelList) is True
        assert received_list == expected_list
