from __future__ import unicode_literals

import datetime

import sqlalchemy.orm
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)

from .depot import MAX_FILE_SIZE, get_current_user
from .model import Object


class Bulletin(Object):
    """Ein Aushang."""

    subject = Column(String)
    content = Column(Text)
    mimetype = Column(String(30), default="")
    size = Column(String(20), default="")
    data = Column(LargeBinary(MAX_FILE_SIZE))
    date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    user_id = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        default=get_current_user,
    )
    user = sqlalchemy.orm.relation("User", uselist=False, backref="bulletins")
