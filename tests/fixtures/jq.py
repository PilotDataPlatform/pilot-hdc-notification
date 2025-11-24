# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from typing import Any

import jq as json_processor
import pytest
from httpx import Response


class JQResult:
    """Typing for jq processor response."""

    def all(self) -> list[Any]:
        pass

    def first(self) -> Any:
        pass

    def text(self) -> str:
        pass


class JQ:
    """Perform jq queries against httpx json response."""

    def __init__(self, response: Response) -> None:
        self.json = response.json()

    def __call__(self, query: str) -> JQResult:
        return json_processor.compile(query).input(self.json)


@pytest.fixture
def jq() -> type[JQ]:
    return JQ
