from __future__ import unicode_literals

import sqlalchemy.orm
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    sql,
)

from .depot import MAX_FILE_SIZE
from .model import Member, Object


class Keylist(Object):
    """Ein Eintrag im Schlüsselbuch."""

    subject = Column(String)


class Key(Object):
    """Ein Schlüssel."""

    keylist_id = Column(
        Integer, ForeignKey(Keylist.id, ondelete="cascade"), nullable=False
    )
    keylist = sqlalchemy.orm.relation(
        "Keylist", uselist=False, backref="keys", cascade="all"
    )

    serial = Column(String)

    member_id = Column(Integer, ForeignKey(Member.id), nullable=True)
    member = sqlalchemy.orm.relation("Member", uselist=False, backref="keys")
    rent = Column(DateTime, nullable=True)
    note = Column(String)
    lost = Column(Boolean, default=sql.false())


class KeyAttachment(Object):
    """Eine Anlage zum Schlüssel."""

    key_id = Column(
        Integer, ForeignKey(Key.id, ondelete="cascade"), nullable=False
    )
    key = sqlalchemy.orm.relation(
        "Key", uselist=False, backref="attachments", cascade="all"
    )
    filename = Column(String(100), default="")
    mimetype = Column(String(30), default="")
    size = Column(String(20), default="")
    data = Column(LargeBinary(MAX_FILE_SIZE))


class KeylistAttachment(Object):
    """Eine Anlage zum Schlüsselbuch."""

    keylist_id = Column(
        Integer, ForeignKey(Keylist.id, ondelete="cascade"), nullable=False
    )
    keylist = sqlalchemy.orm.relation(
        "Keylist", uselist=False, backref="attachments", cascade="all"
    )
    name = Column(String(100), default="")
    mimetype = Column(String(30), default="")
    size = Column(String(20), default="")
    data = Column(LargeBinary(MAX_FILE_SIZE))
