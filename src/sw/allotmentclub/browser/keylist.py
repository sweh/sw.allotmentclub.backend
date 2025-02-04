from __future__ import unicode_literals

import collections
from io import BytesIO

import risclog.sqlalchemy.interfaces
import zope.component
from pyramid.response import FileIter
from pyramid.view import view_config
from sqlalchemy.sql import func, text

import sw.allotmentclub.browser.base
from sw.allotmentclub import (
    Allotment,
    Key,
    KeyAttachment,
    Keylist,
    KeylistAttachment,
    Member,
)

from ..log import log_with_user, user_data_log
from .base import (
    boolean,
    date_time,
    format_mimetype,
    format_size,
    parse_date,
    route_url,
    string_agg,
    to_string,
)


class KeylistQuery(sw.allotmentclub.browser.base.Query):
    data_class = {"Schlüsselbuch": "expand"}

    def select(self):
        return self.db.query(
            Keylist.id.label("#"),
            Keylist.subject.label("Schlüsselbuch"),
        ).select_from(Keylist)


@view_config(route_name="keylists", renderer="json", permission="view")
class KeylistListView(sw.allotmentclub.browser.base.TableView):
    query_class = KeylistQuery
    available_actions = [
        dict(
            url="keylist_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="keylist_edit",
            btn_class="btn-success",
            icon="fa fa-pencil",
            title="Bearbeiten",
        ),
        dict(
            url="keys",
            btn_class="btn-success",
            icon="fa fa-list",
            title="Schlüssel",
        ),
        dict(
            url="keylist_attachment",
            btn_class="btn-success",
            icon="fa fa-list",
            title="Anlagen",
        ),
        dict(
            url="keylist_delete",
            btn_class="btn-danger",
            icon="glyphicon glyphicon-trash",
            title="Löschen",
        ),
    ]


@view_config(route_name="keylist_edit", renderer="json", permission="view")
class KeylistEditView(sw.allotmentclub.browser.base.EditJSFormView):
    title = "Schlüsselbuch bearbeiten"

    @property
    def load_options(self):
        return {"subject": {"label": "Name"}}

    @property
    def load_data(self):
        fields = [("subject", self.context.subject)]
        return collections.OrderedDict(fields)

    def save(self, key, value):
        if key == "rent" and value:
            value = parse_date(value)
        return super(KeylistEditView, self).save(key, value)


@view_config(route_name="keylist_add", renderer="json", permission="view")
class KeylistAddView(KeylistEditView):
    def __init__(self, context, request):
        context = Keylist.create()
        context.commit()
        super(KeylistAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info,
            self.request.user,
            "Schlüsselbuch %s hinzugefügt.",
            self.context.id,
        )

    @property
    def route_name(self):
        return "keylist_edit"


@view_config(route_name="keylist_delete", renderer="json", permission="view")
class KeylistDeleteView(sw.allotmentclub.browser.base.DeleteView):
    model = Keylist

    def update(self):
        db = zope.component.getUtility(risclog.sqlalchemy.interfaces.IDatabase)
        stmt = text("DELETE FROM key WHERE keylist_id = :x")
        stmt = stmt.bindparams(x=self.context.id)
        db.session.execute(stmt)
        stmt = text("DELETE FROM keylistattachment WHERE keylist_id = :x")
        stmt = stmt.bindparams(x=self.context.id)
        db.session.execute(stmt)
        stmt = text("DELETE FROM keylist WHERE id = :x")
        stmt = stmt.bindparams(x=self.context.id)
        db.session.execute(stmt)
        self.deleted = True
        self.result = {"status": "success"}
        self.log()


class KeyQuery(sw.allotmentclub.browser.base.Query):
    formatters = {"Verliehen am": date_time, "Verloren": boolean}
    data_class = {"Seriennummer": "expand"}
    data_hide = {
        "Verloren": "phone,tablet",
        "Notiz": "phone,tablet",
        "Mitglied": "phone",
        "Verliehen am": "phone",
    }

    def select(self):
        return (
            self.db.query(
                Key.id.label("#"),
                Key.serial.label("Seriennummer"),
                (
                    func.coalesce(
                        to_string(Member.lastname)
                        .concat(", ")
                        .concat(
                            to_string(Member.firstname)
                            .concat(" (")
                            .concat(
                                func.coalesce(
                                    string_agg(Allotment.number), "n/a"
                                )
                            )
                        )
                        .concat(")")
                    )
                ).label("Mitglied"),
                Key.rent.label("Verliehen am"),
                Key.note.label("Notiz"),
                Key.lost.label("Verloren"),
            )
            .select_from(Key)
            .outerjoin(Member)
            .outerjoin(Allotment, Allotment.member_id == Member.id)
            .group_by(Key.id, Member.lastname, Member.firstname)
            .filter(Key.keylist == self.context)
        )


@view_config(route_name="keys", renderer="json", permission="view")
class KeysView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Protokolle."""

    query_class = KeyQuery
    default_order_by = "serial"
    available_actions = [
        dict(
            url="key_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="key_edit",
            btn_class="btn-success",
            icon="fa fa-pencil",
            title="Bearbeiten",
        ),
        dict(
            url="key_delete",
            btn_class="btn-danger",
            icon="glyphicon glyphicon-trash",
            title="Löschen",
        ),
    ]


@view_config(route_name="key_edit", renderer="json", permission="view")
class KeyEditView(sw.allotmentclub.browser.base.EditJSFormView):
    title = "Schlüssel bearbeiten"

    @property
    def load_options(self):
        collection_url = "/api/" + route_url(
            "key_list_attachments", self.request
        ).replace("{id}", str(self.context.id)).replace(
            "{keylist_id}", str(self.context.keylist.id)
        )
        return {
            "serial": {"label": "Seriennummer"},
            "member_id": {
                "label": "Mitglied",
                "source": self.member_source,
                "css_class": "chosen",
            },
            "rent": {"label": "Verliehen am", "css_class": "datetimepicker"},
            "note": {"label": "Notiz"},
            "attachment": {
                "label": "Anlage",
                "template": "form_upload",
                "documents_collection_url": collection_url,
            },
            "lost": {"label": "Verloren?", "template": "form_boolean"},
        }

    def resource_data_item(self, item, route_name):
        return {
            "status": "success",
            "resource": self.get_route(item, route_name),
            "id": item.id,
            "data": {"title": self.resource_data_item_title(item)},
        }

    @property
    def load_data(self):
        fields = [
            ("serial", self.context.serial),
            ("member_id", self.context.member_id),
            ("rent", self.context.rent),
            ("note", self.context.note),
            ("lost", self.context.lost),
            (
                "attachment",
                [
                    {"id": a.id, "title": a.filename}
                    for a in self.context.attachments
                ],
            ),
        ]
        return collections.OrderedDict(fields)

    def get_route(self, item, name):
        route = super(KeyEditView, self).get_route(item, name)
        if "key_id" in route:
            route = route.replace("{key_id}", str(self.context.id))
        return route.replace("{keylist_id}", str(self.context.keylist.id))

    def handle_upload(self, file_):
        data = file_.file
        data.seek(0)
        data = data.read()
        return KeyAttachment.create(
            key=self.context,
            filename=file_.filename,
            mimetype=file_.type,
            size=len(data),
            data=data,
        ), "key_attachment_del"


@view_config(
    route_name="key_list_attachments", renderer="json", permission="view"
)
class KeyListAttachments(KeyEditView):
    def update(self):
        self.result = [
            self.resource_data_item(attachment, "key_attachment_del")
            for attachment in self.context.attachments
        ]


@view_config(
    route_name="key_attachment_del", renderer="json", permission="view"
)
class KeyAttachmentDelView(sw.allotmentclub.browser.base.DeleteView):
    model = KeyAttachment

    def update(self):
        db = zope.component.getUtility(risclog.sqlalchemy.interfaces.IDatabase)
        stmt = text("DELETE FROM keyattachment WHERE id = :x")
        stmt = stmt.bindparams(x=self.context.id)
        db.session.execute(stmt)
        self.deleted = True
        self.result = {"status": "success"}
        self.log()


@view_config(
    route_name="key_attachment_download", renderer="json", permission="view"
)
class KeyAttachmentDownloadView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = self.request.response
        response.set_cookie("fileDownload", value="true")
        response.content_type = self.context.mimetype
        response.content_length = int(self.context.size)
        response.content_disposition = 'attachment; filename="{}"'.format(
            self.context.filename
        )
        response.app_iter = FileIter(BytesIO(self.context.data))
        return response


@view_config(route_name="key_add", renderer="json", permission="view")
class KeyAddView(KeyEditView):
    title = "Schlüssel hinzufügen"

    def __init__(self, context, request):
        context = Key.create(keylist=context)
        context.commit()
        super(KeyAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info,
            self.request.user,
            "Schlüssel %s hinzugefügt.",
            self.context.id,
        )

    @property
    def route_name(self):
        return "key_edit"


@view_config(route_name="key_delete", renderer="json", permission="view")
class KeyDeleteView(sw.allotmentclub.browser.base.DeleteView):
    model = Key

    def update(self):
        db = zope.component.getUtility(risclog.sqlalchemy.interfaces.IDatabase)
        stmt = text("DELETE FROM key WHERE id = :x")
        stmt = stmt.bindparams(x=self.context.id)
        db.session.execute(stmt)
        self.deleted = True
        self.result = {"status": "success"}
        self.log()

    def log(self):
        if self.deleted is not None:
            deleted = self.context.id
            keylist = self.context.keylist.subject
            log_with_user(
                user_data_log.info,
                self.request.user,
                "Schlüssel %s aus Schlüsselbuch %s gelöscht.",
                deleted,
                keylist,
            )


class AttachmentQuery(sw.allotmentclub.browser.base.Query):
    formatters = {
        "Größe": format_size,
        "Dateityp": format_mimetype,
    }
    data_class = {"Name": "expand"}
    data_hide = {
        "Dateityp": "phone,tablet",
        "Größe": "phone,tablet",
    }

    def select(self):
        return (
            self.db.query(
                KeylistAttachment.id.label("#"),
                KeylistAttachment.name.label("Name"),
                KeylistAttachment.mimetype.label("Dateityp"),
                KeylistAttachment.size.label("Größe"),
            )
            .select_from(KeylistAttachment)
            .filter_by(keylist=self.context)
        )


@view_config(
    route_name="keylist_attachment", renderer="json", permission="view"
)
class KeylistAttachmentsView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Anlagen."""

    query_class = AttachmentQuery
    default_order_by = "Name"
    available_actions = [
        dict(
            url="keylist_attachment_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="keylist_attachment_download",
            btn_class="btn-success",
            icon="fa fa-download",
            title="Herunterladen",
        ),
    ]


@view_config(
    route_name="keylist_attachment_add", renderer="json", permission="view"
)
class KeylistAttachmentAddView(sw.allotmentclub.browser.base.AddView):
    model = KeylistAttachment

    def parse_file(self):
        file = self.request.params.get("file")
        data = file.file
        data.seek(0)
        data = data.read()
        name = file.filename
        mimetype = file.type
        size = len(data)
        return name, mimetype, size, data

    def log(self, id):
        log_with_user(
            user_data_log.info,
            self.request.user,
            "hat Ablage %s %s.",
            id,
            self.action,
        )

    def __call__(self):
        if not self.form_submit():
            return {"status": "success", "data": {}}
        name, mimetype, size, data = self.parse_file()
        attachment = self.model.create(
            name=name,
            mimetype=mimetype,
            size=size,
            data=data,
            keylist=self.context,
        )
        attachment.commit()
        log_with_user(
            user_data_log.info,
            self.request.user,
            "hat Anlage %s zu Protokoll %s hinzugefügt.",
            attachment.id,
            self.context.id,
        )
        return {"status": "success"}


@view_config(route_name="keylist_attachment_download", permission="view")
class KeylistAttachmentDownloadView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = self.request.response
        response.set_cookie("fileDownload", value="true")
        response.content_type = self.context.mimetype
        response.content_length = int(self.context.size)
        response.content_disposition = (
            "attachment; filename=" + self.context.name
        )
        response.app_iter = FileIter(BytesIO(self.context.data))
        return response
