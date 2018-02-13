# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .model import Object
from sqlalchemy import Column, String, Boolean, Text, sql
import gocept.loginuser.user
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm


class User(Object, gocept.loginuser.user.User):

    unrestricted_access = Column(Boolean, nullable=False, default=sql.false())

    log_entries = sqlalchemy.orm.relation(
        'Log', uselist=True, cascade="all,delete", backref='user')

    # Persönliche Daten
    anrede = Column(String(20), default=u'')
    titel = Column(String(20), default=u'')
    vorname = Column(String(50), default=u'')
    nachname = Column(String(50), default=u'')
    handynummer = Column(String(25), default=u'')
    ort = Column(String(50), default=u'')
    position = Column(String(50), default=u'')
    signature = Column(Text())
    email = Column(String(50), default=u'')
