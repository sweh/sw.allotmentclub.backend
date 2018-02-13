# encoding=utf-8
from __future__ import unicode_literals
from sw.allotmentclub import User


def test_send_mail_sends_html_mail(mailer, database):
    from ..letter import send_mail
    user = User.create(username='hans', vorname='Hans', nachname='Wurst')
    send_mail('sw@gocept.com', 'Betreff', 'Dies ist der Inhalt', user)
    assert 1 == len(mailer.outbox)
    message = mailer.outbox[0]
    assert ('Vorstand Leuna-Bungalowgemeinschaft Roter See '
            '<vorstand@roter-see.de>' == message.sender)
    assert ['sw@gocept.com'] == message.recipients
    assert message.body == (
        '\nDies ist der Inhalt\n\nMit freundlichen Grüßen,\n'
        'Im Auftrag des Vorstandes\n\nHans Wurst (None)')
    assert message.html.startswith(
        '\n<html lang="de">\n<head>\n<meta charset="utf-8"/>\n'
        '<style>\n    body { font-size: 12pt; }')
