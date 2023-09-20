# Copyright (C) 2022-2023 Indoc Systems

# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html. 
# You may not use this file except in compliance with the License.

from uuid import uuid4

from sqlalchemy import VARCHAR
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from notification.components.db_model import DBModel


class Announcement(DBModel):
    """Announcement database model."""

    __tablename__ = 'announcements'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4)
    effective_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer(), nullable=False)
    message = Column(VARCHAR(length=512), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    announcement_unsubscriptions = relationship(
        'AnnouncementUnsubscription', back_populates='announcement', cascade='all, delete-orphan', passive_deletes=True
    )


class AnnouncementUnsubscription(DBModel):
    """Announcement unsubscription database model."""

    __tablename__ = 'announcement_unsubscriptions'
    __table_args__ = (UniqueConstraint('announcement_id', 'username', name='announcement_id_username_unique'),)

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4)
    announcement_id = Column(
        postgresql.UUID(as_uuid=True), ForeignKey('announcements.id', ondelete='CASCADE'), nullable=False
    )
    username = Column(VARCHAR(length=256), nullable=False)

    announcement = relationship('Announcement', back_populates='announcement_unsubscriptions')
