# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .depot import MAX_FILE_SIZE
from .model import Object, Member
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Boolean, sql, LargeBinary)
import sqlalchemy.orm


class Keylist(Object):
    """Ein Eintrag im Schlüsselbuch."""

    subject = Column(String)


class Key(Object):
    """Ein Schlüssel."""

    keylist_id = Column(
        Integer, ForeignKey(Keylist.id, ondelete='cascade'), nullable=False)
    keylist = sqlalchemy.orm.relation(
        'Keylist', uselist=False, backref='keys', cascade='all')

    serial = Column(String)

    member_id = Column(Integer, ForeignKey(Member.id), nullable=True)
    member = sqlalchemy.orm.relation('Member', uselist=False, backref='keys')
    rent = Column(DateTime, nullable=True)
    note = Column(String)
    lost = Column(Boolean, default=sql.false())


class KeylistAttachment(Object):
    """Eine Anlage zum Schlüsselbuch."""

    keylist_id = Column(
        Integer, ForeignKey(Keylist.id, ondelete='cascade'), nullable=False)
    keylist = sqlalchemy.orm.relation(
        'Keylist', uselist=False, backref='attachments', cascade='all')
    name = Column(String(100), default=u'')
    mimetype = Column(String(30), default=u'')
    size = Column(String(20), default=u'')
    data = Column(LargeBinary(MAX_FILE_SIZE))
