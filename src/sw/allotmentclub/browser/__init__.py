import risclog.sqlalchemy.serializer

from .session import patch as session_patch

risclog.sqlalchemy.serializer.patch()
session_patch()
