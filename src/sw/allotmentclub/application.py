import risclog.sqlalchemy.db

from sw.allotmentclub.model import ENGINE_NAME


class Application(object):
    settings = None
    testing = False

    @classmethod
    def from_filename(cls, filename):
        """Creates a portal from a paste.ini file."""
        # We have to do the import here because the converter cannot depend
        # on pyramid:
        import pyramid.paster

        pyramid.paster.setup_logging(filename)
        settings = pyramid.paster.get_appsettings(filename)
        portal = cls(**settings)
        portal.configure()
        portal.setup_runtime()
        return portal

    def __init__(self, testing=False, **settings):
        self.settings = settings
        self.settings["testing"] = testing
        self.testing = testing

    def __call__(self, **settings):
        self.settings.update(settings)
        self.configure()
        self.setup_runtime()
        # can't go into setup_runtime, since initialize_db uses that, too
        self.check_db_revision()

    def setup_runtime(self):
        if not self.testing:
            db = risclog.sqlalchemy.db.get_database()
            db.register_engine(
                self.settings["sqlalchemy.url"],
                engine_args=dict(pool_pre_ping=True),
                name=ENGINE_NAME,
                alembic_location="sw.allotmentclub:alembic",
            )

    def check_db_revision(self):
        db = risclog.sqlalchemy.db.get_database(self.testing)
        try:
            db.assert_database_revision_is_current(ENGINE_NAME)
        except ValueError:
            # Bail out when database revision does not match.
            raise SystemExit(
                "Database revision does not match current head. "
                "Please run alembic to get migrated to the latest revision."
            )

    def configure(self):
        pass
