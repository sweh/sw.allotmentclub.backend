from __future__ import unicode_literals

import gocept.loginuser.user
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm
from sqlalchemy import Boolean, Column, String, Text, sql

from .model import Object


class User(Object, gocept.loginuser.user.User):
    unrestricted_access = Column(Boolean, nullable=False, default=sql.false())

    log_entries = sqlalchemy.orm.relation(
        "Log", uselist=True, cascade="all,delete", backref="user"
    )

    # Persönliche Daten
    anrede = Column(String(20), default="")
    titel = Column(String(20), default="")
    vorname = Column(String(50), default="")
    nachname = Column(String(50), default="")
    handynummer = Column(String(25), default="")
    ort = Column(String(50), default="")
    position = Column(String(50), default="")
    signature = Column(Text())
    email = Column(String(50), default="")
