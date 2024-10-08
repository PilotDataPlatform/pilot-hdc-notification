# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from notification.components.pagination import Page
from notification.components.pagination import Pagination


class TestPagination:
    def test_is_disabled_returns_true_when_page_size_is_zero(self):
        pagination = Pagination(page_size=0)

        assert pagination.is_disabled() is True

    def test_is_disabled_returns_false_when_page_size_is_not_zero(self):
        pagination = Pagination(page_size=1)

        assert pagination.is_disabled() is False


class TestPage:
    def test_total_pages_returns_0_when_page_size_is_zero(self):
        pagination = Pagination(page_size=0)
        page = Page(pagination=pagination, count=0, entries=[])
        assert page.total_pages == 0

    def test_total_pages_returns_non_zero_when_page_size_is_not_zero(self):
        pagination = Pagination(page_size=2)
        page = Page(pagination=pagination, count=2, entries=[])
        assert page.total_pages == 1
