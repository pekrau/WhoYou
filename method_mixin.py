""" WhoYou: Simple accounts database for web applications.

Mixin class for methods: authentication and database connection.
"""

import logging
import sqlite3

from wrapid.fields import *
from wrapid.response import *
from wrapid.utils import basic_authentication
from wrapid.resource import Resource, GET, POST

from . import configuration
from .database import Database, Account, Team


class MethodMixin(object):
    "Mixin class for Method subclasses; database connect and authentication."

    def prepare(self, resource, request, application):
        "Connect to the database and authenticate the user."
        self.db = Database()
        self.db.open()
        try:
            name, password = basic_authentication(request,
                                                  application.name,
                                                  require=True)
            self.login = self.db.get_account(name, password=password)
        except (KeyError, ValueError):
            raise HTTP_UNAUTHORIZED_BASIC_CHALLENGE(realm=application.name)

    def finalize(self):
        self.db.close()

    def get_data_basic(self, resource, request, application):
        "Return a dictionary with the basic data for the resource."
        links = []
        if self.is_admin():
            links.append(dict(title='Accounts',
                              resource='Account list',
                              href=application.get_url('accounts')))
        links.append(dict(title='My account',
                          resource='Account',
                          href=application.get_url('account', self.login.name)))
        if self.is_admin():
            links.append(dict(title='Teams',
                              resource='Team list',
                              href=application.get_url('teams')))
        links.append(dict(title='Documentation',
                          resource='Documentation',
                          href=application.get_url('doc')))
        return dict(application=dict(name=application.name,
                                     version=application.version,
                                     href=application.url,
                                     host=configuration.HOST),
                    resource=resource.type,
                    href=resource.url,
                    links=links,
                    outreprs=self.get_outrepr_links(resource, application),
                    loginname=self.login.name)

    def is_admin(self):
        "Is the login account 'admin' or member of the 'admin' team?"
        if self.login.name == 'admin': return True
        team = self.db.get_team('admin')
        if team:
            return team.is_member(self.login)
        else:
            return False

    def allow_admin(self):
        "Raise HTTP FORBIDDEN if login account is not admin."
        if not self.is_admin():
            raise HTTP_FORBIDDEN("'admin' login required")

    def is_access(self):
        "Is the login account allowed to access this method of the resource?"
        return True

    def allow_access(self):
        "Raise HTTP FORBIDDEN if login account is not allowed to read this."
        if not self.is_access():
            raise HTTP_FORBIDDEN("disallowed for login '%s'" % self.login)

    def get_account(self, variables):
        """Get the account instance according to the variables data.
        Handle the case where an account name containing a dot and
        a short (<=4 chars) last name, which will be confused for
        a format specification.
        Returns None if no account could be identified.
        """
        try:
            return Account(self.db, variables['account'])
        except KeyError:
            return None
        except ValueError:
            if variables.get('FORMAT'):
                name = variables['account'] + variables['FORMAT']
                try:
                    result = Account(self.db, name)
                except ValueError:
                    return None
                else:
                    variables['account'] += variables['FORMAT']
                    variables['FORMAT'] = None
                    return result
        return None

    def get_team(self, variables):
        """Get the team instance according to the variables data.
        Handle the case where an team name containing a dot and
        a short (<=4 chars) last name, which will be confused for
        a format specification.
        Returns None if no team could be identified.
        """
        try:
            return Team(self.db, variables['team'])
        except KeyError:
            return None
        except ValueError:
            if variables.get('FORMAT'):
                name = variables['team'] + variables['FORMAT']
                try:
                    result = Team(self.db, name)
                except ValueError:
                    return None
                else:
                    variables['team'] += variables['FORMAT']
                    variables['FORMAT'] = None
                    return result
        return None
