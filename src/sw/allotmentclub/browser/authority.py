from __future__ import unicode_literals

import collections

from pyramid.view import view_config

import sw.allotmentclub.browser.base
from sw.allotmentclub import AccessAuthority, User

from .base import boolean, get_view_for_route
from .navigation import NAVIGATION_ITEMS


class AuthorityContext(object):
    id = None

    @classmethod
    def context_factory(cls, request):
        import sw.allotmentclub.browser.auth

        result = cls()
        result.id = request.matchdict["id"]
        result.__acl__ = sw.allotmentclub.browser.auth.authorize()
        return result


@view_config(route_name="access_authority", renderer="json", permission="view")
class AccessAuthorityListView(sw.allotmentclub.browser.base.View):
    """Liste aller Routen für die Berechtigungsaussteuerung."""

    def add_sub_actions(self, items, id):
        parent = id
        view = get_view_for_route(id.replace("_group", ""), self.request)
        for act in getattr(view.__original_view__, "available_actions", []):
            items.append((act["url"], act["title"], parent, {}, act["icon"]))
            items = self.add_sub_actions(items, act["url"])
        return items

    def update(self):
        data = []
        items = []  # id, text, parent, state, icon
        for text, id, icon, children in NAVIGATION_ITEMS:
            parent = "#"
            if id == "access_authority":
                continue
            state = dict()
            if children is not None:
                state["disabled"] = True
            items.append((id, text, parent, state, icon))
            if "disabled" not in state:
                items = self.add_sub_actions(items, id)
            parent = id
            if children is None:
                continue
            if "disabled" in state:
                parent = parent + "_group"
            for text, id in children:
                items.append((id, text, parent, {}, icon))
                items = self.add_sub_actions(items, id)

        for id, text, parent, state, icon in items:
            if "disabled" in state:
                id = id + "_group"
            if "glyphicon" not in icon:
                icon = "fa fa-lg fa-fw {}".format(icon)
            data.append(
                dict(id=id, text=text, parent=parent, state=state, icon=icon)
            )
        self.result = dict(data=data, status="success")


class Query(sw.allotmentclub.browser.base.Query):
    formatters = {
        "Gesperrt": boolean,
    }

    def select(self):
        return (
            self.db.query(
                AccessAuthority.id.label("#"),
                User.username.label("User"),
                User.nachname.label("Nachname"),
                User.vorname.label("Vorname"),
                User.is_locked.label("Gesperrt"),
            )
            .select_from(AccessAuthority)
            .join(User)
            .filter(AccessAuthority.viewname == self.context.id)
        )


@view_config(
    route_name="access_authority_detail", renderer="json", permission="view"
)
class AccessAuthorityDetailsView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Zugriffsberechtigungen für einen View."""

    query_class = Query
    available_actions = [
        dict(
            url="access_authority_detail_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="access_authority_detail_delete",
            btn_class="btn-danger",
            icon="glyphicon glyphicon-trash",
            title="Löschen",
        ),
    ]


@view_config(
    route_name="access_authority_detail_edit",
    renderer="json",
    permission="view",
)
class AccessAuthorityDetailEditView(
    sw.allotmentclub.browser.base.EditJSFormView
):
    title = "Berechtigung hinzufügen"

    @property
    def users(self):
        query = super(AccessAuthorityDetailEditView, self).users
        query = query.filter(User.unrestricted_access.is_(False))
        return query

    @property
    def load_options(self):
        return {
            "user_id": {
                "label": "Benutzer",
                "source": self.user_source,
                "css_class": "chosen",
                "required": True,
            },
        }

    @property
    def load_data(self):
        fields = [
            ("user_id", self.context.user_id),
        ]
        return collections.OrderedDict(fields)

    def get_route(self, item, name):
        route = super(AccessAuthorityDetailEditView, self).get_route(
            item, name
        )
        return route.replace("{viewname}", self.context.viewname)


@view_config(
    route_name="access_authority_detail_add",
    renderer="json",
    permission="view",
)
class AccessAuthorityDetailAddView(AccessAuthorityDetailEditView):
    title = "Berechtigung bearbeiten"

    def __init__(self, context, request):
        context = AccessAuthority.create(viewname=context.id)
        context.commit()
        super(AccessAuthorityDetailAddView, self).__init__(context, request)

    @property
    def route_name(self):
        return "access_authority_detail_edit"


@view_config(
    route_name="access_authority_detail_delete",
    renderer="json",
    permission="view",
)
class AccessAuthorityDetailDeleteView(
    sw.allotmentclub.browser.base.DeleteView
):
    model = AccessAuthority
