def test_no_route_to_energy_meter_import_if_not_logged_in(browser):
    browser.open("http://localhost/navigation")
    assert "energy_meter_import" not in str(browser.json["data"])


def test_route_to_access_authority_if_logged_in_as_admin(browser):
    browser.login()
    browser.open("http://localhost/navigation")
    assert "access_authority" in str(browser.json["data"])


def test_no_route_to_access_authority_if_logged_in_as_non_admin(browser):
    import transaction

    from ...user import User

    User.create(username="user", password="user", unrestricted_access=False)
    transaction.commit()

    browser.login(username="user", password="user")
    browser.open("http://localhost/navigation")
    assert "access_authority" not in str(browser.json["data"])


def test_route_to_configured_route_if_logged_in_as_non_admin(browser):
    import transaction

    from ...model import AccessAuthority
    from ...user import User

    user = User.create(
        username="user", password="user", unrestricted_access=False
    )
    AccessAuthority.find_or_create(viewname="access_authority", user=user)

    transaction.commit()

    browser.login(username="user", password="user")
    browser.open("http://localhost/navigation")
    assert "access_authority" in str(browser.json["data"])
