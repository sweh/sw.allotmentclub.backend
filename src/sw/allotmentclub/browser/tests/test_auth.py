import sw.allotmentclub.version


def test_no_access_if_not_logged_in(browser):
    browser.open("http://localhost/login")
    assert {
        "message": "",
        "status": "error",
        "version": sw.allotmentclub.version.__version__,
    } == browser.json


def test_login_is_possible(browser):
    browser.login()
    result = browser.json
    assert "Anmeldung erfolgreich." == result["message"]
    assert "success" == result["status"]
    assert sw.allotmentclub.version.__version__ == result["version"]
    assert {
        "gravatar": (
            "https://www.gravatar.com/avatar/"
            "d41d8cd98f00b204e9800998ecf8427e"
        ),
        "name": "Admin istrator",
        "username": "admin",
    } == result["user"]


def test_no_access_if_logging_in_with_invalid_data(browser):
    browser.login(username="admin", password="wrong")
    assert {
        "message": "Anmeldung fehlgeschlagen.",
        "status": "error",
        "version": sw.allotmentclub.version.__version__,
    } == browser.json


def test_double_login_not_possible(browser):
    browser.login()
    browser.login()
    assert "Ihre Sitzung wurde wiederhergestellt." == browser.json["message"]


def test_logout_is_possible(browser):
    browser.login()
    browser.open("http://localhost/logout")
    assert {
        "message": (
            "Abmeldung abgeschlossen. Sie können sich nun " "erneut anmelden."
        ),
        "status": "success",
        "version": sw.allotmentclub.version.__version__,
    } == browser.json
