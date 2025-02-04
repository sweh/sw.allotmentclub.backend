from ..log import auth_log, log_with_user
from ..user import User


def patch():
    from beaker.session import Session

    Session._load_orig = Session.load
    Session.load = load


def load(self):
    """Monkey Patch to generate logs for sessions which timed out"""
    # load session data without timeout check
    import pyramid.threadlocal

    self.namespace = self.namespace_class(
        self.id,
        data_dir=self.data_dir,
        digest_filenames=False,
        **self.namespace_args,
    )
    self.namespace.acquire_read_lock()
    session_data = None
    try:
        try:
            session_data = self.namespace["session"]
        except (KeyError, TypeError):
            pass  # new session
    finally:
        self.namespace.release_read_lock()

    # call original method
    self._load_orig()

    # log message if session with user id existed and timeout was reached
    if (
        session_data is not None
        and "auth.userid" in session_data
        and self.was_invalidated
    ):
        user = User.get(session_data["auth.userid"])
        log_with_user(
            auth_log.info,
            user,
            "Session for user %s timed out.",
            user.username,
        )
        # mark timeout on request to display flash message later on
        request = pyramid.threadlocal.get_current_request()
        request.session_timeout = True
