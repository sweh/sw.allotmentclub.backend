# encoding=utf-8
from __future__ import unicode_literals
from .depot import MAX_FILE_SIZE
from .model import PersonMixin, Member, members_messages_table
from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, Text
from sqlalchemy import DateTime, LargeBinary, Table
from sqlalchemy.orm import relationship
from sw.allotmentclub import Object
import sqlalchemy.orm


externals_messages_table = Table(
    'externals_messages', Object.metadata,
    Column('external_id', Integer, ForeignKey('externalrecipient.id')),
    Column('message_id', Integer, ForeignKey('message.id'))
)


class Message(Object):
    """A mail or pdf message."""

    members = relationship("Member", secondary=members_messages_table)
    externals = relationship("ExternalRecipient",
                             secondary=externals_messages_table)
    inbound = Column(Boolean, nullable=False, default=False)
    subject = Column(String(255))
    body = Column(Text)
    user_id = Column(
        Integer, ForeignKey('user.id'), nullable=False)
    user = sqlalchemy.orm.relation('User', uselist=False)
    printed = Column(DateTime)
    sent = Column(DateTime)
    accounting_year = Column(Integer)

    in_reply_to_id = Column(
        Integer, ForeignKey('message.id'), nullable=True)
    in_reply_to = sqlalchemy.orm.relationship('Message', uselist=False)

    attachments = sqlalchemy.orm.relationship(
        'Attachment', uselist=True,
        cascade="all,delete", back_populates='message')

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

    message_id = Column(
        Integer, ForeignKey('message.id'), nullable=False)
    message = sqlalchemy.orm.relationship(
        'Message', uselist=False, back_populates='attachments')
    filename = Column(String(100), default=u'')
    mimetype = Column(String(100), default=u'')
    size = Column(String(20), default=u'')
    data = Column(LargeBinary(MAX_FILE_SIZE))
    white_page_before = Column(Boolean, default=False, nullable=False)


class SentMessageInfo(Object):
    """Additional info for messages sent via email."""

    message_id = Column(
        Integer, ForeignKey('message.id'), nullable=False)
    message = sqlalchemy.orm.relationship('Message', uselist=False)
    tag = Column(String(100))
    address = Column(String(100))
    status = Column(String(255))


class ExternalRecipient(Object, PersonMixin):
    """An external recipient for messages."""

    title = Column(String(20), default=u'')
    appellation = Column(String(20), default=u'')
    firstname = Column(String(50), default=u'')
    lastname = Column(String(50), default=u'')
    street = Column(String(100), default=u'')
    zip = Column(String(6), default=u'')
    city = Column(String(50), default=u'')
    country = Column(String(50), default=u'')
    email = Column(String(100), default=u'')

    messages = relationship("Message", secondary=externals_messages_table)
