from __future__ import unicode_literals

import datetime
import hashlib

from babel.dates import format_datetime
from pyramid.view import view_config

import sw.allotmentclub.browser.base
from sw.allotmentclub import Log, User


class Query(sw.allotmentclub.browser.base.Query):
    def select(self):
        return (
            self.db.query(
                Log.created.label("Datum"),
                Log.user_id.label("Benutzer"),
                Log.name.label("Typ"),
                Log.msg.label("Nachricht"),
            )
            .select_from(Log)
            .filter(
                Log.created
                >= (datetime.datetime.now() - datetime.timedelta(days=14))
            )
            .filter(Log.user_id != 1)
        )


def format_date(dt):
    now = datetime.datetime.now()
    if dt > now - datetime.timedelta(minutes=15):
        return "gerade eben"
    if dt.date() == now.date():
        return "heute"
    if dt.date() == (now - datetime.timedelta(days=1)).date():
        return "gestern"
    return (format_datetime(dt, "EEEE, d.M.Y", locale="de_DE"),)


@view_config(route_name="home", renderer="json", permission="view")
class HomeView(sw.allotmentclub.browser.base.TableView):
    query_class = Query
    default_order_by = "created"
    default_sort_direction = "desc"

    def __call__(self):
        result = super(HomeView, self).__call__()
        last = None
        timeline = []
        for date, user_id, type_, msg in sw.allotmentclub.json_result(
            result["data"]["data"]
        ):
            if timeline:
                last = timeline[-1]
            time = format_date(date)
            user = User.get(user_id)
            username = user.username
            if last and last["username"] == username and last["time"] == time:
                if msg == last["detail"][-1]:
                    continue
                last["detail"].append(msg)
            else:
                item = {
                    "time": time,
                    "username": username,
                    "firstname": user.vorname,
                    "lastname": user.nachname,
                    "detail": [msg],
                }
                if username == "system":
                    item["fa_icon"] = "fa-gear"
                else:
                    item["gravatar_url"] = (
                        "https://www.gravatar.com/avatar/%s"
                        % (hashlib.md5(user.email.encode("utf-8")).hexdigest())
                    )
                timeline.append(item)
        result["data"]["timeline"] = timeline
        return result
