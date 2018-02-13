# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .model import Object
from sqlalchemy import (
    Column, Integer, String, ForeignKey, LargeBinary, DateTime)
import sqlalchemy.orm

MAX_FILE_SIZE = 1024*1024*10  # 10 MB


def get_current_user(*args, **kw):
    import pyramid
    return pyramid.threadlocal.get_current_request().user.id


class Depot(Object):
    """ Die Ablage."""

    name = Column(String(100), default=u'')
    mimetype = Column(String(30), default=u'')
    size = Column(String(20), default=u'')
    data = Column(LargeBinary(MAX_FILE_SIZE))
    date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False,
                     default=get_current_user)
    user = sqlalchemy.orm.relation(
        'User', uselist=False, backref='depot_items')
