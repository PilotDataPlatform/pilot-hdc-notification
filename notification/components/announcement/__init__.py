# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from notification.components.announcement.models import Announcement
from notification.components.announcement.models import AnnouncementUnsubscription
from notification.components.announcement.views import router as announcement_router

__all__ = [
    'Announcement',
    'AnnouncementUnsubscription',
    'announcement_router',
]
