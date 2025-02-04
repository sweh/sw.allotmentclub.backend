from __future__ import unicode_literals

import datetime

import sqlalchemy.orm
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from sw.allotmentclub import Object

from .depot import MAX_FILE_SIZE, get_current_user
from .model import Member, PersonMixin, members_messages_table

externals_messages_table = Table(
    "externals_messages",
    Object.metadata,
    Column("external_id", Integer, ForeignKey("externalrecipient.id")),
    Column("message_id", Integer, ForeignKey("message.id")),
)


class Message(Object):
    """A mail or pdf message."""

    members = relationship("Member", secondary=members_messages_table)
    externals = relationship(
        "ExternalRecipient", secondary=externals_messages_table
    )
    inbound = Column(Boolean, nullable=False, default=False)
    subject = Column(String(255))
    body = Column(Text)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = sqlalchemy.orm.relation("User", uselist=False)
    printed = Column(DateTime)
    sent = Column(DateTime)
    accounting_year = Column(Integer)

    in_reply_to_id = Column(Integer, ForeignKey("message.id"), nullable=True)
    in_reply_to = sqlalchemy.orm.relationship("Message", uselist=False)

    attachments = sqlalchemy.orm.relationship(
        "Attachment",
        uselist=True,
        cascade="all,delete",
        back_populates="message",
    )

    @property
    def member_ids(self):
        return [m.id for m in self.members]

    @member_ids.setter
    def member_ids(self, value):
        self.members = [Member.get(m) for m in value]

    @property
    def external_ids(self):
        return [e.id for e in self.externals]

    @external_ids.setter
    def external_ids(self, value):
        self.externals = [ExternalRecipient.get(e) for e in value]


class Attachment(Object):
    """An attachment for a message."""

    message_id = Column(Integer, ForeignKey("message.id"), nullable=False)
    message = sqlalchemy.orm.relationship(
        "Message", uselist=False, back_populates="attachments"
    )
    filename = Column(String(100), default="")
    mimetype = Column(String(100), default="")
    size = Column(String(20), default="")
    data = Column(LargeBinary(MAX_FILE_SIZE))
    white_page_before = Column(Boolean, default=False, nullable=False)
    date = Column(DateTime, nullable=True, default=datetime.datetime.now)
    user_id = Column(
        Integer, ForeignKey("user.id"), nullable=True, default=get_current_user
    )
    user = sqlalchemy.orm.relation(
        "User", uselist=False, backref="attachments"
    )


class SentMessageInfo(Object):
    """Additional info for messages sent via email."""

    message_id = Column(Integer, ForeignKey("message.id"), nullable=False)
    message = sqlalchemy.orm.relationship("Message", uselist=False)
    tag = Column(String(150))
    address = Column(String(100))
    status = Column(String(255))


class ExternalRecipient(Object, PersonMixin):
    """An external recipient for messages."""

    title = Column(String(20), default="")
    appellation = Column(String(20), default="")
    organization = Column(String(100), default="")
    firstname = Column(String(50), default="")
    lastname = Column(String(50), default="")
    street = Column(String(100), default="")
    zip = Column(String(6), default="")
    city = Column(String(50), default="")
    country = Column(String(50), default="")
    email = Column(String(100), default="")
    phone = Column(String(50), default="")
    deleted = Column(Boolean, default=False)

    messages = relationship("Message", secondary=externals_messages_table)
