""" WhoYou: Simple accounts database for web applications.

Unit tests for the web resource API.
"""

import httplib

from wrapid.testbase import *


URL = 'http://localhost/whoyou'
ACCOUNT = 'test'
PASSWORD = 'abc123'


class TestAccess(TestBase):
    "Check basic access."

    def test_GET_home_HTML(self):
        "Fetch the home page, in HTML format."
        wr = self.get_wr('text/html')
        response = wr.GET('/')
        self.assertEqual(response.status, httplib.OK,
                         msg="HTTP status %s" % response.status)
        headers = self.get_headers(response)
        self.assert_(headers.get('content-type').startswith('text/html'))

    def test_GET_home_JSON(self):
        "Fetch the home page, in JSON format."
        response = self.wr.GET('/')
        self.assertEqual(response.status, httplib.OK,
                         msg="HTTP status %s" % response.status)
        headers = self.get_headers(response)
        self.assert_(headers['content-type'].startswith('application/json'),
                     msg=headers['content-type'])
        self.get_json_data(response)

    def test_GET_home_XYZ(self):
        "Try fetching the home page in an impossible format."
        wr = self.get_wr('text/xyz')
        response = wr.GET('/')
        self.assertEqual(response.status, httplib.NOT_ACCEPTABLE,
                         msg="HTTP status %s" % response.status)

    def test_GET_nonexistent(self):
        "Try fetching a non-existent resource."
        response = self.wr.GET('/doesnotexist')
        self.assertEqual(response.status, httplib.NOT_FOUND,
                         msg="HTTP status %s" % response.status)


class TestAccount(TestBase):
    "Test account handling."

    def test_GET_accounts(self):
        "Try fetching accounts list for non-admin test user."
        response = self.wr.GET('/accounts')
        self.assertEqual(response.status, httplib.FORBIDDEN,
                         msg="HTTP status %s" % response.status)

    def test_GET_account(self):
        "Fetch the data for this account, in JSON format."
        response = self.wr.GET("/account/%s" % self.wr.account)
        self.assertEqual(response.status, httplib.OK,
                         msg="HTTP status %s" % response.status)
        headers = self.get_headers(response)
        self.assert_(headers['content-type'].startswith('application/json'),
                     msg=headers['content-type'])
        self.get_json_data(response)

    def test_GET_account_admin(self):
        "Try fetching 'admin' account data."
        response = self.wr.GET('/account/admin')
        self.assertEqual(response.status, httplib.FORBIDDEN,
                         msg="HTTP status %s" % response.status)


if __name__ == '__main__':
    ex = TestExecutor(url=URL, account=ACCOUNT, password=PASSWORD)
    print 'Testing', ex.wr
    ex.test(TestAccess,
            TestAccount)
