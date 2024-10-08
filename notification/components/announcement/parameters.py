# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Query

from notification.components.announcement.filtering import AnnouncementFiltering
from notification.components.parameters import FilterParameters
from notification.components.parameters import SortByFields


class AnnouncementSortByFields(SortByFields):
    """Fields by which announcements can be sorted."""

    EFFECTIVE_DATE = 'effective_date'
    CREATED_AT = 'created_at'


class AnnouncementFilterParameters(FilterParameters):
    """Query parameters for announcements filtering."""

    username: str | None = Query(default=None)

    def to_filtering(self) -> AnnouncementFiltering:
        return AnnouncementFiltering(username=self.username)
