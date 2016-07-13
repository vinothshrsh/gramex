import requests
from . import server
from . import TestGramex


class TestURLPriority(TestGramex):
    'Test Gramex URL priority sequence'

    def test_url_priority(self):
        self.check('/path/abc', text='/path/.*')
        self.check('/path/file', text='/path/file')
        self.check('/path/dir', text='/path/.*')
        self.check('/path/dir/', text='/path/dir/.*')
        self.check('/path/dir/abc', text='/path/dir/.*')
        self.check('/path/dir/file', text='/path/dir/file')
        self.check('/path/priority', text='/path/priority')


class TestURLNormalization(TestGramex):
    'Test URL pattern normalization'

    def test_url_normalization(self):
        self.check('/path/norm1', text='/path/norm1')
        self.check('/path/norm2', text='/path/norm2')


class TestAttributes(TestGramex):
    'Ensure that BaseHandler subclasses have relevant attributes'

    def test_attributes(self):
        self.check('/func/attributes', code=200)


class TestXSRF(TestGramex):
    'Test BaseHandler xsrf: setting'

    def test_xsrf(self):
        r = self.check('/path/norm')
        self.assertFalse('Set-Cookie' in r.headers)

        # First request sets xsrf cookie
        session = requests.Session()
        r = session.get(server.base_url + '/xsrf', timeout=10)
        self.assertTrue('Set-Cookie' in r.headers)
        self.assertTrue('_xsrf' in r.headers['Set-Cookie'])

        # Next request does not set xsrf cookie, because it already exists
        r = session.get(server.base_url + '/xsrf', timeout=10)
        self.assertFalse('Set-Cookie' in r.headers)
