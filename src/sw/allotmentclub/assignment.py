# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .model import Object
from .base import format_eur
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
import sqlalchemy.orm


class Assignment(Object):
    """ Der Arbeitseinsatz. """

    purpose = Column(String(254))
    responsible_id = Column(Integer, ForeignKey('member.id'), nullable=True)
    responsible = sqlalchemy.orm.relation(
        'Member', uselist=False, backref='responsible_for')
    day = Column(DateTime)
    accounting_year = Column(Integer)
    attendees = sqlalchemy.orm.relation(
        'AssignmentAttendee', uselist=True, backref='assignment',
        cascade='all,delete')


class AssignmentAttendee(Object):
    """ Teilnehmer an einem Arbeitseinsatz."""

    assignment_id = Column(
        Integer, ForeignKey('assignment.id'), nullable=False)
    member_id = Column(
        Integer, ForeignKey('member.id'), nullable=True)
    member = sqlalchemy.orm.relation(
        'Member', uselist=False, backref='assignments')
    hours = Column(Float(1), nullable=True)


class AssignmentTodo(Object):
    """ Eine (mögliche) Tätigkeit beim Arbeitseinsatz. """

    description = Column(String, nullable=True)
    priority = Column(Integer, nullable=False, default=4)


def get_assignment_mail_data(member, year):
    if member.leaving_year or not member.allotments:
        return
    price = int((5 - member.assignment_hours) * 10) * 10000
    if price <= 0:
        return
    content_data = dict(
        assignment_hours=member.assignment_hours,
        to_pay=format_eur(price),
        year=year,
        iban=member.iban,
        iban_short=(
            member.iban.replace(member.iban[:18], 'X'*18)
            if member.iban else None
        ),
        bic=member.bic,
        direct_debit=member.direct_debit)
    subject = u'Fehlende Arbeitsstunden %s' % year
    yield subject, content_data
