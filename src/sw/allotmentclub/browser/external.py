# encoding=utf8
from __future__ import unicode_literals
from ..log import user_data_log, log_with_user
from .base import to_string
from pyramid.view import view_config
from sw.allotmentclub import ExternalRecipient
from sqlalchemy import or_, and_
import collections
import sw.allotmentclub.browser.base


def filter_external_recipients(query):
    return (
        query.filter(
            or_(
                and_(
                    ExternalRecipient.city != '',
                    ExternalRecipient.city.isnot(None),
                ),
                and_(
                    ExternalRecipient.email != '',
                    ExternalRecipient.email.isnot(None),
                )
            )
        )
        .filter(
            and_(
                ExternalRecipient.lastname != '',
                ExternalRecipient.lastname.isnot(None),
            )
        )
        .filter(ExternalRecipient.deleted.isnot(True))
    )


class Query(sw.allotmentclub.browser.base.Query):

    formatters = {}
    data_class = {
        'Nachname': 'expand'
    }
    data_hide = {
        'Vorname': 'phone,tablet',
        'Adresse': 'phone,tablet',
        'E-Mail': 'phone',
    }

    def select(self):
        return filter_external_recipients(
            self.db.query(
                ExternalRecipient.id.label('#'),
                ExternalRecipient.organization.label('Firma'),
                ExternalRecipient.lastname.label('Nachname'),
                ExternalRecipient.firstname.label('Vorname'),
                (
                    to_string(ExternalRecipient.street).concat('<br />')
                    .concat(to_string(ExternalRecipient.zip)).concat(' ')
                    .concat(to_string(ExternalRecipient.city))
                ).label('Adresse'),
                ExternalRecipient.email.label('E-Mail'),
            )
            .select_from(ExternalRecipient)
        )


@view_config(route_name='externals', renderer='json',
             permission='view')
class ExternalRecipientListView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    default_order_by = 'lastname'
    available_actions = [
        dict(url='external_add', btn_class='btn-success', icon='fa fa-plus',
             title='Neu'),
        dict(url='external_edit', btn_class='btn-success', icon='fa fa-pencil',
             title='Bearbeiten'),
        dict(url='external_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen')]


@view_config(route_name='external_edit', renderer='json',
             permission='view')
class ExternalRecipientEditView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Externen Empfänger bearbeiten'

    @property
    def load_options(self):
        return {
            'title': {
                'label': 'Titel',
                'required': True,
                'source': [
                    {'title': '', 'token': ''},
                    {'title': 'Dr.', 'token': 'Dr.'},
                    {'title': 'Dr. med.', 'token': 'Dr. med.'},
                    {'title': 'Prof. Dr.', 'token': 'Prof. Dr.'}
                ]},
            'appellation': {
                'required': True,
                'label': 'Anrede',
                'source': [
                    {'title': '', 'token': ''},
                    {'title': 'Herr', 'token': 'Herr'},
                    {'title': 'Frau', 'token': 'Frau'}
                ]},
            'organization': {'label': 'Firma'},
            'firstname': {'label': 'Vorname', 'required': True},
            'lastname': {'label': 'Nachname', 'required': True},
            'street': {'label': 'Straße'},
            'zip': {'label': 'PLZ'},
            'city': {'label': 'Stadt'},
            'country': {'label': 'Land'},
            'email': {'label': 'E-Mail'},
            'phone': {'label': 'Telefon'},
        }

    @property
    def load_data(self):
        fields = [
            ('appellation', self.context.appellation),
            ('title', self.context.title),
            ('organization', self.context.organization),
            ('firstname', self.context.firstname),
            ('lastname', self.context.lastname),
            ('street', self.context.street),
            ('zip', self.context.zip),
            ('city', self.context.city),
            ('country', self.context.country),
            ('email', self.context.email),
            ('phone', self.context.phone),

        ]
        return collections.OrderedDict(fields)


@view_config(route_name='external_add', renderer='json',
             permission='view')
class ExternalRecipientAddView(ExternalRecipientEditView):

    title = 'Externen Empfänger anlegen'

    def __init__(self, context, request):
        context = ExternalRecipient.create()
        context.commit()
        super(ExternalRecipientAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info, self.request.user,
            'Externen Empfänger %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'external_edit'


@view_config(route_name='external_delete', renderer='json',
             permission='view')
class ExternalRecipientDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = ExternalRecipient
    mark_deleted = True
