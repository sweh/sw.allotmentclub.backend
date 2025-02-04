from __future__ import unicode_literals

import collections

from pyramid.view import view_config
from sqlalchemy import func

import sw.allotmentclub.browser.base
from sw.allotmentclub import (
    Allotment,
    Assignment,
    AssignmentAttendee,
    AssignmentTodo,
    Member,
)

from ..log import log_with_user, user_data_log
from .base import (
    date_time,
    datetime_now,  # noqa
    get_selected_year,
    string_agg,
    to_string,
)

PRIORITIES = [
    {"token": 1, "title": "Sofort"},
    {"token": 2, "title": "Dringend"},
    {"token": 3, "title": "Hoch"},
    {"token": 4, "title": "Normal"},
    {"token": 5, "title": "Niedrig"},
]


class Query(sw.allotmentclub.browser.base.Query):
    formatters = {
        "Datum": date_time,
    }

    data_class = {"Datum": "expand"}
    data_hide = {
        "Zweck": "phone,tablet",
        "Verantwortlich": "tablet",
    }

    def select(self):
        assignments = (
            self.db.query(
                Assignment.id.label("#"),
                Assignment.day.label("Datum"),
                Assignment.purpose.label("Zweck"),
                to_string(Member.lastname)
                .concat(", ")
                .concat(to_string(Member.firstname))
                .label("Verantwortlich"),
            )
            .select_from(Assignment)
            .join(Member)
            .filter(Assignment.accounting_year == get_selected_year())
        )
        return assignments


@view_config(route_name="assignments", renderer="json", permission="view")
class AssignmentListView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Arbeitseinsätze, filterbar nach Jahr."""

    query_class = Query
    default_order_by = "day"
    year_selection = True
    start_year = 2015
    available_actions = [
        dict(
            url="assignment_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="assignment_edit",
            btn_class="btn-success",
            icon="fa fa-pencil",
            title="Bearbeiten",
        ),
        dict(
            url="assignment_delete",
            btn_class="btn-danger",
            icon="glyphicon glyphicon-trash",
            title="Löschen",
            callback="sw.allotmentclub.assignments_list_view.render()",
        ),
        dict(
            url="assignment_list_attendees",
            btn_class="btn-success",
            icon="fa fa-list",
            title="Teilnehmer",
        ),
    ]


@view_config(route_name="assignment_edit", renderer="json", permission="view")
class AssignmentEditView(sw.allotmentclub.browser.base.EditJSFormView):
    title = "Arbeitseinsatz bearbeiten"

    @property
    def load_options(self):
        return {
            "day": {"label": "Tag", "css_class": "datetimepicker"},
            "purpose": {
                "label": "Zweck",
            },
            "responsible_id": {
                "label": "Verantwortlich",
                "source": self.member_source,
                "css_class": "chosen",
                "required": True,
            },
        }

    @property
    def load_data(self):
        fields = [
            ("day", date_time(self.context.day)),
            ("purpose", self.context.purpose),
            ("responsible_id", self.context.responsible_id),
        ]
        return collections.OrderedDict(fields)


@view_config(route_name="assignment_add", renderer="json", permission="view")
class AssignmentAddView(AssignmentEditView):
    title = "Arbeitseinsatz anlegen"

    def __init__(self, context, request):
        context = Assignment.create(accounting_year=get_selected_year())
        context.commit()
        super(AssignmentAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info,
            self.request.user,
            "Arbeitseinsatz %s hinzugefügt.",
            self.context.id,
        )

    @property
    def route_name(self):
        return "assignment_edit"


@view_config(
    route_name="assignment_delete", renderer="json", permission="view"
)
class AssignmentDeleteView(sw.allotmentclub.browser.base.DeleteView):
    model = Assignment


class QueryAttendees(sw.allotmentclub.browser.base.Query):
    def select(self):
        return (
            self.db.query(
                AssignmentAttendee.id.label("#"),
                to_string(Member.lastname)
                .concat(", ")
                .concat(to_string(Member.firstname))
                .label("Teilnehmer"),
                AssignmentAttendee.hours.label("Stunden"),
            )
            .select_from(AssignmentAttendee)
            .join(Member)
            .filter(AssignmentAttendee.assignment == self.context)
        )


@view_config(
    route_name="assignment_list_attendees", renderer="json", permission="view"
)
class AssignmentListAttendeesView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Teilnehmer zu einem Arbeitseinsatz."""

    query_class = QueryAttendees
    default_order_by = "lastname"
    available_actions = [
        dict(
            url="assignment_attendees_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="assignment_attendees_edit",
            btn_class="btn-success",
            icon="fa fa-pencil",
            title="Bearbeiten",
        ),
        dict(
            url="assignment_attendees_delete",
            btn_class="btn-danger",
            icon="glyphicon glyphicon-trash",
            title="Löschen",
            callback="sw.allotmentclub.assignment_attendees_view.render()",
        ),
    ]


@view_config(
    route_name="assignment_attendees_edit", renderer="json", permission="view"
)
class AssignmentAttendeesEditView(
    sw.allotmentclub.browser.base.EditJSFormView
):
    title = "Stunden für Teilnehmer erfassen"

    @property
    def load_options(self):
        return {
            "member_id": {
                "label": "Mitglied",
                "source": self.member_source,
                "css_class": "chosen",
                "required": True,
            },
            "hours": {"label": "geleistete Stunden"},
        }

    @property
    def load_data(self):
        fields = [
            ("member_id", self.context.member_id),
            ("hours", self.context.hours),
        ]
        return collections.OrderedDict(fields)

    def save(self, key, value):
        if value and key == "hours":
            value = value.replace(",", ".")
        return super(AssignmentAttendeesEditView, self).save(key, value)

    def get_route(self, item, name):
        route = super(AssignmentAttendeesEditView, self).get_route(item, name)
        return route.replace(
            "{assignment_id}", str(self.context.assignment.id)
        )


@view_config(
    route_name="assignment_attendees_add", renderer="json", permission="view"
)
class AssignmentAttendeesAddView(AssignmentAttendeesEditView):
    model = AssignmentAttendee

    def __init__(self, context, request):
        context = AssignmentAttendee.create(assignment=context)
        super(AssignmentAttendeesAddView, self).__init__(context, request)

    @property
    def route_name(self):
        return "assignment_attendees_edit"


@view_config(
    route_name="assignment_attendees_delete",
    renderer="json",
    permission="view",
)
class AssignmentAttendeesDeleteView(sw.allotmentclub.browser.base.DeleteView):
    model = AssignmentAttendee

    def log(self):
        if self.deleted is not None:
            deleted = self.context.member
            assignment = self.context.assignment.id
            log_with_user(
                user_data_log.info,
                self.request.user,
                "%s %s von Arbeitseinsatz %s gestrichen.",
                deleted.firstname,
                deleted.lastname,
                assignment,
            )


class MemberAssignmentQuery(sw.allotmentclub.browser.base.Query):
    formatters = {
        "Stunden": lambda mid, request: Member.get(mid).assignment_hours,
    }
    data_class = {"Mitglied": "expand"}
    data_hide = {
        "Stunden": "phone",
    }

    def select(self):
        return (
            self.db.query(
                Member.id.label("#"),
                (
                    to_string(Member.lastname)
                    .concat(", ")
                    .concat(
                        to_string(Member.firstname)
                        .concat(" (")
                        .concat(
                            func.coalesce(string_agg(Allotment.number), "n/a")
                        )
                        .concat(")")
                    )
                ).label("Mitglied"),
                Member.id.label("Stunden"),
            )
            .select_from(Allotment)
            .join(Member, Allotment.member_id == Member.id)
            .group_by(Member.id)
        )


@view_config(
    route_name="member_assignments", renderer="json", permission="view"
)
class MemberAssignmentView(sw.allotmentclub.browser.base.TableView):
    query_class = MemberAssignmentQuery
    year_selection = True
    start_year = 2015

    available_actions = [
        dict(
            url="member_assignments_detail",
            btn_class="btn-success",
            icon="fa fa-list",
            title="Details",
        ),
        dict(
            url="member_assignments_bill",
            btn_class="btn-danger",
            icon="fa fa-bank",
            title="Abrechnen",
        ),
    ]


class MemberAssignmentDetailQuery(sw.allotmentclub.browser.base.Query):
    formatters = {"Datum": date_time}

    data_class = {"Einsatz": "expand"}

    def select(self):
        return (
            self.db.query(
                AssignmentAttendee.id.label("#"),
                Assignment.purpose.label("Einsatz"),
                Assignment.day.label("Datum"),
                AssignmentAttendee.hours.label("Stunden"),
            )
            .select_from(AssignmentAttendee)
            .join(Assignment)
            .filter(AssignmentAttendee.member == self.context)
            .filter(Assignment.accounting_year == get_selected_year())
        )


@view_config(
    route_name="member_assignments_detail", renderer="json", permission="view"
)
class MemberAssignmentsDetailListView(sw.allotmentclub.browser.base.TableView):
    query_class = MemberAssignmentDetailQuery
    year_selection = True


@view_config(
    route_name="member_assignments_bill", renderer="json", permission="view"
)
class MemberAssignmentsBillView(sw.allotmentclub.browser.base.View):
    def update(self):
        for member in self.active_members.all():
            member.bill_assignment_hours()
        self.result = {
            "status": "success",
            "message": "Arbeitsstunden erfolgreich übertragen",
        }


def fmt_priority(value, request):
    for i in PRIORITIES:
        if i["token"] == value:
            return i["title"]


class TodoQuery(sw.allotmentclub.browser.base.Query):
    formatters = {
        "Priorität": fmt_priority,
    }

    def select(self):
        todos = self.db.query(
            AssignmentTodo.id.label("#"),
            AssignmentTodo.priority.label("Priorität"),
            AssignmentTodo.description.label("Aufgabe"),
        ).select_from(AssignmentTodo)
        return todos


@view_config(route_name="assignment_todos", renderer="json", permission="view")
class AssignmentTodoListView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Tätigkeiten."""

    query_class = TodoQuery
    default_order_by = "priority"
    year_selection = False
    available_actions = [
        dict(
            url="assignment_todo_add",
            btn_class="btn-success",
            icon="fa fa-plus",
            title="Neu",
        ),
        dict(
            url="assignment_todo_edit",
            btn_class="btn-success",
            icon="fa fa-pencil",
            title="Bearbeiten",
        ),
        dict(
            url="assignment_todo_delete",
            btn_class="btn-danger",
            icon="glyphicon glyphicon-trash",
            title="Löschen",
            callback="sw.allotmentclub.assignments_list_view.render()",
        ),
    ]


@view_config(
    route_name="assignment_todo_edit", renderer="json", permission="view"
)
class AssignmentTodoEditView(sw.allotmentclub.browser.base.EditJSFormView):
    title = "Tätigkeit bearbeiten"

    @property
    def load_options(self):
        return {
            "priority": {
                "label": "",
                "source": self.priority_source,
                "css_class": "chosen",
                "required": True,
            },
            "description": {
                "label": "Beschreibung",
            },
        }

    @property
    def priority_source(self):
        return PRIORITIES

    @property
    def load_data(self):
        fields = [
            ("priority", self.context.priority),
            ("description", self.context.description),
        ]
        return collections.OrderedDict(fields)


@view_config(
    route_name="assignment_todo_add", renderer="json", permission="view"
)
class AssignmentTodoAddView(AssignmentTodoEditView):
    title = "Tätigkeit anlegen"

    def __init__(self, context, request):
        context = AssignmentTodo.create()
        context.commit()
        super(AssignmentTodoAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info,
            self.request.user,
            "Tätigkeit %s hinzugefügt.",
            self.context.id,
        )

    @property
    def route_name(self):
        return "assignment_todo_edit"


@view_config(
    route_name="assignment_todo_delete", renderer="json", permission="view"
)
class AssignmentTodoDeleteView(sw.allotmentclub.browser.base.DeleteView):
    model = AssignmentTodo
