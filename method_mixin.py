""" WhoYou: Simple accounts database for web applications.

Mixin class for methods: authentication and database connection.
"""

from wrapid.fields import *
from wrapid.responses import *
from wrapid.methods import GET, POST, RedirectMixin
from wrapid.login import LoginMixin

from . import configuration
from .database import Database, Account, Team


class MethodMixin(LoginMixin):
    "Mixin class for Method subclasses; database connect and authentication."

    def prepare(self, request):
        "Connect to the database and authenticate the user."
        self.db = Database()
        self.db.open()      # Database must be open before logging in.
        self.set_login(request)
        self.set_current(request)
        self.check_access()

    def get_account(self, name, password=None):
        """Return a dictionary describing the account:
        name, description, email, teams and properties.
        If password is provided, authenticate the account.
        Raise KeyError if there is no such account.
        Raise ValueError if the password does not match.
        """
        return self.db.get_account(name, password).get_data()

    def get_account_anonymous(self):
        "Anonymous login is disallowed."
        raise KeyError

    def finalize(self):
        self.db.close()

    def set_current(self, request):
        "Set the current entities to operate on."
        pass

    def check_access(self):
        "Raise HTTP FORBIDDEN if login account is not allowed to read this."
        if not self.is_accessible():
            raise HTTP_FORBIDDEN("disallowed for login '%(name)s'" % self.login)

    def is_accessible(self):
        "Is the login account allowed to access this method of the resource?"
        return True

    def is_login_admin(self):
        "Is the login account 'admin' or member of the 'admin' team?"
        if self.login['name'] == 'admin': return True
        team = self.db.get_team('admin')
        if team:
            return team.is_member(self.db.get_account(self.login['name']))
        else:
            return False

    def get_data_links(self, request):
        "Return the links response data."
        get_url = request.application.get_url
        links = []
        if self.is_login_admin():
            links.append(dict(title='Accounts',
                              resource='Account list',
                              href=get_url('accounts')))
        links.append(dict(title='My account',
                          resource='Account',
                          href=get_url('account', self.login['name'])))
        if self.is_login_admin():
            links.append(dict(title='Teams',
                              resource='Team list',
                              href=get_url('teams')))
        links.append(dict(title='Documentation: API',
                          resource='Documentation API',
                          href=get_url('doc')))
        return links
