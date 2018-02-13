# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .model import Object
from sqlalchemy import (
    Column, Integer, Text, String, ForeignKey, LargeBinary, DateTime)
from .depot import MAX_FILE_SIZE, get_current_user
import datetime
import sqlalchemy.orm


class Bulletin(Object):
    """Ein Aushang."""

    subject = Column(String)
    content = Column(Text)
    mimetype = Column(String(30), default=u'')
    size = Column(String(20), default=u'')
    data = Column(LargeBinary(MAX_FILE_SIZE))
    date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False,
                     default=get_current_user)
    user = sqlalchemy.orm.relation(
        'User', uselist=False, backref='bulletins')
