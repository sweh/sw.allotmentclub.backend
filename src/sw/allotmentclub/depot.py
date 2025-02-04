import sqlalchemy.orm
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)

from .model import MAX_FILE_SIZE, Object


def get_current_user(*args, **kw):
    import pyramid

    user = pyramid.threadlocal.get_current_request().user
    if user:
        return user.id


class Depot(Object):
    """Die Ablage."""

    name = Column(String(100), default="")
    category = Column(String(100), default="")
    mimetype = Column(String(100), default="")
    size = Column(String(20), default="")
    data = Column(LargeBinary(MAX_FILE_SIZE))
    date = Column(DateTime, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        default=get_current_user,
    )
    user = sqlalchemy.orm.relation(
        "User", uselist=False, backref="depot_items"
    )
