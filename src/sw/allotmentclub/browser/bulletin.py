from __future__ import unicode_literals

import collections

from pyramid.view import view_config

import sw.allotmentclub.browser.base
import sw.allotmentclub.browser.letter
from sw.allotmentclub import Bulletin, User

from ..log import log_with_user, user_data_log
from .base import date_time
from .protocol import format_markdown


class Query(sw.allotmentclub.browser.base.Query):
    formatters = {
        "Datum": date_time,
    }

    data_class = {"Betreff": "expand"}
    data_hide = {
        "Datum": "phone,tablet",
        "Von": "phone,tablet",
    }

    def select(self):
        return (
            self.db.query(
                Bulletin.id.label("#"),
                Bulletin.subject.label("Betreff"),
                Bulletin.date.label("Datum"),
                User.username.label("Von"),
            )
            .select_from(Bulletin)
            .join(User)
        )


@view_config(route_name="bulletins", renderer="json", permission="view")
class BulletinListView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Aushänge."""

    query_class = Query
    default_order_by = "date"
    available_actions = [
        dict(
            url="bulletin_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="bulletin_edit",
            btn_class="btn-success",
            icon="fa fa-pencil",
            title="Bearbeiten",
        ),
        dict(
            url="bulletin_delete",
            btn_class="btn-danger",
            icon="glyphicon glyphicon-trash",
            title="Löschen",
        ),
        dict(
            url="bulletin_print",
            btn_class="btn-success",
            icon="fa fa-print",
            title="Herunterladen",
        ),
    ]


@view_config(route_name="bulletin_edit", renderer="json", permission="view")
class BulletinEditView(sw.allotmentclub.browser.base.EditJSFormView):
    title = "Aushang bearbeiten"

    @property
    def load_options(self):
        return {
            "subject": {
                "label": "Betreff",
            },
            "content": {
                "label": "Inhalt",
                "template": "form_markdown",
            },
        }

    @property
    def load_data(self):
        fields = [
            ("subject", self.context.subject),
            ("content", self.context.content),
        ]
        return collections.OrderedDict(fields)


@view_config(route_name="bulletin_add", renderer="json", permission="view")
class BulletinAddView(BulletinEditView):
    def __init__(self, context, request):
        context = Bulletin.create()
        context.commit()
        super(BulletinAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info,
            self.request.user,
            "Aushang %s hinzugefügt.",
            self.context.id,
        )

    @property
    def route_name(self):
        return "bulletin_edit"


@view_config(route_name="bulletin_delete", renderer="json", permission="view")
class BulletinDeleteView(sw.allotmentclub.browser.base.DeleteView):
    model = Bulletin


@view_config(route_name="bulletin_print", permission="view")
class BulletinPrintView(sw.allotmentclub.browser.base.PrintBaseView):
    filename = "Aushang"

    def get_pdf(self):
        data = self.get_json(self.context)
        content = format_markdown(
            "# {}\n\n{}".format(data["subject"], data["content"])
        )
        content = '<div style="padding-top: 10pt">%s</div>' % content
        data["content"] = content
        return sw.allotmentclub.browser.letter.render_pdf(
            None,
            None,
            data["content"],
            self.context.user,
            self.context.date,
            font_size="16pt",
        )
