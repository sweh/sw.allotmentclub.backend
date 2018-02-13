# encoding=utf8
from __future__ import unicode_literals
import pyramid.testing
import pyramid_mailer
import pytest
import sw.allotmentclub.browser.app
import sw.allotmentclub.browser.testing
import sw.allotmentclub.conftest


DEFAULT_SETTINGS = {
    'beaker.lock_dir': '/tmp',
    'https_disabled': 'true',
    'public_server_name': 'localhost',
    'pyramid.default_locale_name': 'de_DE',
    'pyramid_deform.tempdir': '/tmp',
    'pyramid.render_traceback': 'true',
    'contact_default_recipients': 'vorstand@roter-see.de',
    'bitbtl.secret': 'secret',
    'bitbtl.quality': 5,
}


@pytest.fixture(scope='session')
def portal_app(database_session):
    """Create a portal app."""
    return sw.allotmentclub.browser.app.Portal(
        testing=True, **DEFAULT_SETTINGS)


@pytest.fixture(scope='session')
def wsgi_app(portal_app):
    """Create the congress WSGI app."""
    return portal_app({})


@pytest.fixture(scope='function')
def browser(wsgi_app, verwalter):
    """Get a zope.testbrowser for the WSGI-APP."""
    return sw.allotmentclub.browser.testing.Browser(wsgi_app=wsgi_app)


@pytest.fixture(scope='function')
def dummy_request(portal_app, wsgi_app):
    """Get a request with the current app."""
    registry = portal_app.config.registry
    request = pyramid.testing.DummyRequest(_registry=registry)
    context = pyramid.threadlocal.manager.get().copy()
    context['request'] = request
    context['registry'] = registry
    pyramid.threadlocal.manager.push(context)
    return pyramid.testing.DummyRequest(_registry=registry)


@pytest.fixture(scope='function')
def mailer(dummy_request):
    """Get the pyramid_mailer testing mailer."""
    mailer = pyramid_mailer.get_mailer(dummy_request)
    mailer.outbox = []
    return mailer
