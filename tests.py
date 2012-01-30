""" WhoYou: Simple accounts database for web applications.

Unit tests for the web resource API.
"""

from wrapid.testbase import *


ROOT = '/whoyou'
ACCOUNT = 'test'
PASSWORD = 'abc123'


class TestAccess(TestBase):
    "Check basic access."

    def test_GET_home_HTML(self):
        "Fetch the home page, in HTML format."
        response = self.GET('/', accept='text/html')
        self.assertEqual(response.status, httplib.OK,
                         msg="HTTP status %s" % response.status)
        headers = wsgiref.headers.Headers(response.getheaders())
        self.assert_(headers.get('content-type').startswith('text/html'))

    def test_GET_home_JSON(self):
        "Fetch the home page, in JSON format."
        response = self.GET('/')
        self.assertEqual(response.status, httplib.OK,
                         msg="HTTP status %s" % response.status)
        headers = wsgiref.headers.Headers(response.getheaders())
        self.assert_(headers.get('content-type') == 'application/json')
        self.get_json_data(response)

    def test_GET_home_XYZ(self):
        "Try fetching the home page in an impossible format."
        response = self.GET('/', accept='text/xyz')
        self.assertEqual(response.status, httplib.NOT_ACCEPTABLE,
                         msg="HTTP status %s" % response.status)

    def test_GET_nonexistent(self):
        "Try fetching a non-existent resource."
        response = self.GET('/doesnotexist')
        self.assertEqual(response.status, httplib.NOT_FOUND,
                         msg="HTTP status %s" % response.status)


class TestAccount(TestBase):
    "Test account handling."

    def test_GET_accounts(self):
        "Try fetching accounts list for non-admin test user."
        response = self.GET('/accounts')
        self.assertEqual(response.status, httplib.FORBIDDEN,
                         msg="HTTP status %s" % response.status)

    def test_GET_account(self):
        "Fetch the data for this account, in JSON format."
        response = self.GET("/account/%s" % self.configuration.account)
        self.assertEqual(response.status, httplib.OK,
                         msg="HTTP status %s" % response.status)
        headers = wsgiref.headers.Headers(response.getheaders())
        self.assert_(headers.get('content-type') == 'application/json')
        try:
            data = json.loads(response.read())
        except ValueError:
            self.fail('invalid JSON data')

    def test_GET_account_admin(self):
        "Try fetching 'admin' account data."
        response = self.GET('/account/admin')
        self.assertEqual(response.status, httplib.FORBIDDEN,
                         msg="HTTP status %s" % response.status)


if __name__ == '__main__':
    ex = TestExecutor(root=ROOT, account=ACCOUNT, password=PASSWORD)
    print "Testing http://%s/%s ...\n" % (ex.netloc, ex.root)
    ex.test(TestAccess,
            TestAccount)
