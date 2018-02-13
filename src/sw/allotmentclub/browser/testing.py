# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from zope.testbrowser.wsgi import Browser
import json
import sw.allotmentclub


class Browser(Browser):
    """Our enhanced browser."""

    username = 'admin'
    password = 'admin'

    @property
    def json(self):
        return json.loads(self.contents.decode('utf-8'))

    def open(self, url, data=None, xhr=False):
        if xhr:
            self.addXhrHeader()
        super(Browser, self).open(url, data)

    def post(self, url, data, type='json', xhr=False):
        """Type can be

            `json` … convert data to JSON + set content_type
            `plain` … use data as it is."""
        if xhr:
            self.addXhrHeader()
        content_type = None
        if type == 'json':
            content_type = 'application/json'
            data = json.dumps(data)
        elif type != 'plain':
            content_type = type
        super(Browser, self).post(url, data, content_type)

    def get(self, url, xhr=False):
        if xhr:
            self.addXhrHeader()
        super(Browser, self).open(url)

    def _upload(self, url, filedata=None):
        if filedata is None:
            from io import BytesIO
            filedata = (
                'Transparent.gif', 'image/gif',
                BytesIO(
                    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff'
                    b'\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01'
                    b'\x00\x01\x00\x00\x02\x01D\x00'))
        self.post(
            url,
            type=(
                'multipart/form-data; boundary='
                '---------------------------13041189051108335053514081693'),
            data=(b'-----------------------------13041189051108335053514081693'
                  b'\r\nContent-Disposition: form-data; name="file"; '
                  b'filename="%b"\r\nContent-type: %b\r\n\r\n%b;\r\n'
                  b'-----------------------------13041189051108335053514081693'
                  b'--') % (filedata[0].encode(),
                            filedata[1].encode(),
                            filedata[2].read()))

    def login(self, username=None, password=None):
        """Log in via browser."""
        if username is None:
            username = self.username
        if password is None:
            password = self.password

        self.post(
            'http://localhost/login',
            'username=%s&password=%s' % (username, password),
            'plain')

    def logout(self):
        self.open('http://localhost/logout')

    def addXhrHeader(self):
        self.addHeader('X_REQUESTED_WITH', 'XMLHttpRequest')

    @property
    def json_result(self):
        return sw.allotmentclub.json_result(self.json['data']['data'])
