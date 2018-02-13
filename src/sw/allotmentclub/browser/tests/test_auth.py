# encoding=utf-8
import sw.allotmentclub.version


def test_no_access_if_not_logged_in(browser):
    browser.open('http://localhost/login')
    assert {
        u'message': u'',
        u'status': u'error',
        u'version': sw.allotmentclub.version.__version__
    } == browser.json


def test_login_is_possible(browser):
    browser.login()
    result = browser.json
    assert 'Anmeldung erfolgreich.' == result['message']
    assert 'success' == result['status']
    assert sw.allotmentclub.version.__version__ == result['version']
    assert {
        u'gravatar': (u'https://www.gravatar.com/avatar/'
                      u'd41d8cd98f00b204e9800998ecf8427e'),
        u'name': u'Admin istrator',
        u'username': u'admin'
    } == result['user']


def test_no_access_if_logging_in_with_invalid_data(browser):
    browser.login(username='admin', password='wrong')
    assert {
        u'message': u'Anmeldung fehlgeschlagen.',
        u'status': u'error',
        u'version': sw.allotmentclub.version.__version__
    } == browser.json


def test_double_login_not_possible(browser):
    browser.login()
    browser.login()
    assert u'Ihre Sitzung wurde wiederhergestellt.' == browser.json['message']


def test_logout_is_possible(browser):
    browser.login()
    browser.open('http://localhost/logout')
    assert {
        u'message': (u'Abmeldung abgeschlossen. Sie können sich nun '
                     u'erneut anmelden.'),
        u'status': u'success',
        u'version': sw.allotmentclub.version.__version__
    } == browser.json
