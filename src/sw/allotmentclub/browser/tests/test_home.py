# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import transaction


def test_displays_list_of_log_entries(browser):
    from sw.allotmentclub import Log, User
    User.create(id=2, username='sw', vorname='Sebastian',
                nachname='Wehrmann')
    Log.create(user_id=2, name='user data', level='INFO',
               created=datetime.datetime.now(), msg='Test-Log-Eintrag')
    transaction.commit()

    browser.login()
    browser.open('http://localhost/')
    assert {
        'username': 'sw',
        'firstname': 'Sebastian',
        'lastname': 'Wehrmann',
        'gravatar_url': 'https://www.gravatar.com/avatar/'
                        'd41d8cd98f00b204e9800998ecf8427e',
        'detail': ['Test-Log-Eintrag'],
        'time': 'gerade eben'
    } in browser.json['data']['timeline']


def test_fa_icon_if_system_user(browser):
    from sw.allotmentclub import Log, User
    user = User.find_or_create(username='system')
    Log.create(user=user, name='user data', level='INFO',
               created=datetime.datetime.now(), msg='Test-Log-Eintrag')
    transaction.commit()

    browser.login()
    browser.open('http://localhost/')
    timeline = browser.json['data']['timeline'][0]
    assert timeline['fa_icon'] == 'fa-gear'
    assert 'gravatar_url' not in timeline
