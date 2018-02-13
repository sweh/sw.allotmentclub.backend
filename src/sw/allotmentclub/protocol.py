# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .depot import MAX_FILE_SIZE
from .model import Object
from sqlalchemy import (
    ForeignKey, Column, String, DateTime, Text, Integer, LargeBinary)
import sqlalchemy.orm


class Protocol(Object):
    """ Das Protokoll. """

    title = Column(String(254))
    location = Column(String(254))
    attendees = Column(String(254))
    day = Column(DateTime)
    accounting_year = Column(Integer)
    details = sqlalchemy.orm.relation(
        'ProtocolDetail', uselist=True, backref='protocol',
        order_by="ProtocolDetail.id", cascade='all,delete')
    attachments = sqlalchemy.orm.relation(
        'ProtocolAttachment', uselist=True, backref='protocol',
        order_by="ProtocolAttachment.name", cascade='all,delete')
    commitments = sqlalchemy.orm.relation(
        'ProtocolCommitment', uselist=True, backref='protocol',
        cascade='all,delete')


class ProtocolDetail(Object):
    """ Ein Protokoll-Eintrag. """

    protocol_id = Column(
        Integer, ForeignKey('protocol.id'), nullable=False)
    duration = Column(Integer, nullable=False, server_default='0')
    message = Column(Text, nullable=False, server_default='')
    responsible = Column(String(2), nullable=False, server_default='')


class ProtocolAttachment(Object):
    """ Eine Anlage zum Protokoll. """

    protocol_id = Column(
        Integer, ForeignKey('protocol.id'), nullable=False)
    name = Column(String(100), default=u'')
    mimetype = Column(String(30), default=u'')
    size = Column(String(20), default=u'')
    data = Column(LargeBinary(MAX_FILE_SIZE))


class ProtocolCommitment(Object):
    """ Eine Anlage zum Protokoll. """

    protocol_id = Column(
        Integer, ForeignKey('protocol.id'), nullable=False)
    who = Column(String(254))
    what = Column(String(254))
    when = Column(String(254))
