""" WhoYou: Simple accounts database for web applications.

Account resource.
"""

import string
import pprint

from . import configuration
from .database import Account
from .method_mixin import *
from .representation import *


class AccountsHtmlRepresentation(HtmlRepresentation):
    "HTML representation of the accounts list."

    def get_content(self):
        rows = [TR(TH('Name'),
                   TH('Email'),
                   TH('Teams'))]
        for account in self.data['accounts']:
            teams = []
            for team in account['teams']:
                name = team['name']
                if team['is_admin']:
                    name += ' (admin)'
                teams.append(str(A(name, href=team['href'])))
            rows.append(TR(TD(A(account['name'], href=account['href'])),
                           TD(account.get('email') or ''),
                           TD(', '.join(teams))))
        return TABLE(klass='list', *rows)


class GET_Accounts(MethodMixin, GET):
    "The list of accounts."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                AccountsHtmlRepresentation]

    def is_accessible(self):
        return self.is_login_admin()

    def get_data_resource(self, resource, request, application):
        data = dict(title='Accounts')
        data['accounts'] = []
        for account in self.db.get_accounts():
            accountdata = account.get_data()
            accountdata['href'] = application.get_url('account', account)
            accountdata['teams'] = []
            for team in account.get_teams():
                teamdata = dict(name=str(team),
                                href=application.get_url('team', team),
                                is_admin=team.is_admin(account))
                accountdata['teams'].append(teamdata)
            data['accounts'].append(accountdata)
        data['operations'] = [dict(title='Create account',
                                   href=application.get_url('account'))]
        return data


class AccountHtmlRepresentation(HtmlRepresentation):
    "HTML representation of the account data."

    def get_content(self):
        account = self.data['account']
        teams = []
        for team in account['teams']:
            name = team['name']
            if team['is_admin']:
                name += ' (admin)'
            teams.append(str(A(name, href=team['href'])))
        table = TABLE()
        table.append(TR(TH('Description'),
                        TD(markdown_to_html(account.get('description')))))
        table.append(TR(TH('Teams'),
                        TD(', '.join(teams))))
        table.append(TR(TH('Email'),
                        TD(account.get('email') or '')))
        table.append(TR(TH('Properties'),
                        TD(PRE(pprint.pformat(account.get('properties'))))))
        return table


class AccountMixin(object):
    "Mixin class to set the account to operate on."

    def set_current(self, resource, request, application):
        """Set the account to operate on.
        This handles the case where an account name contains a dot
        and a short (<=4 chars) last name, which will otherwise
        be confused for a FORMAT specification.
        """
        variables = resource.variables
        try:
            self.account = Account(self.db, variables['account'])
        except KeyError:
            if not variables.get('FORMAT'):
                raise HTTP_NOT_FOUND
            name = variables['account'] + variables['FORMAT']
            try:
                self.account = Account(self.db, name)
            except KeyError:
                raise HTTP_NOT_FOUND
            else:
                resource.undo_format_specifier('account')

    def is_login_account(self):
        "Is the login account the same as the account to operate on?"
        return self.login['name'] == self.account.name


class GET_Account(AccountMixin, MethodMixin, GET):
    "Data for an account."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                AccountHtmlRepresentation]

    def is_accessible(self):
        return self.is_login_admin() or self.is_login_account()

    def get_data_operations(self, resource, request, application):
        "Return the operations response data."
        return [dict(title='Edit account',
                     href=application.get_url('account',
                                              self.account.name,
                                              'edit'))]

    def get_data_resource(self, resource, request, application):
        data = dict(title="Account %s" % self.account,
                    account=self.account.get_data())
        teams = []
        for name in data['account'].pop('teams'):
            is_admin = self.db.get_team(name).is_admin(self.account)
            teams.append(dict(name=name,
                              href=application.get_url('team', name),
                              is_admin=is_admin))
        data['account']['teams'] = teams
        return data


class GET_AccountEdit(AccountMixin, MethodMixin, GET):
    "Edit an account."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                FormHtmlRepresentation]

    fields = (PasswordField('password', title='Current password',
                            required=True,
                            descr='Must be provided to effect any change.'),
              PasswordField('new_password', title='New password',
                            descr="If blank, then password will not be changed."
                            " If given, must be at least %s characters." %
                            configuration.MIN_PASSWORD_LENGTH),
              PasswordField('confirm_new_password',
                            title='Confirm new password',
                            descr='Must be given if a new password'
                            ' is specified above.'),
              StringField('email', title='Email', length=30),
              TextField('description', title='Description'),
              MultiSelectField('teams', title='Teams',
                               check=False,
                               descr='Indicate team memberships'
                               ' for the account.'),
              HiddenField('url', descr='Referring URL.'))

    def is_accessible(self):
        return self.is_login_admin() or self.is_login_account()

    def get_data_resource(self, resource, request, application):
        data = dict(title="Edit account %s" % self.account)
        values = dict(name=self.account.name,
                      email=self.account.email,
                      description=self.account.description)
        if self.is_login_admin():
            skip = set(['password'])
            fill = dict(teams=dict(options=[str(t)
                                            for t in self.db.get_teams()]))
            default = dict(teams=[str(t) for t in self.account.get_teams()])
        else:
            skip = set()
            fill = dict()
            default = dict()
        default['url'] = request.headers['Referer'] or \
                         application.get_url('account', self.account)
        data['form'] = dict(fields=self.get_fields_data(skip=skip,
                                                        fill=fill,
                                                        default=default),
                            values=values,
                            title='Modify account data',
                            label='Save',
                            href=resource.get_url(),
                            cancel=application.get_url('account',
                                                       self.account.name))
        return data


class POST_AccountEdit(AccountMixin, MethodMixin, RedirectMixin, POST):
    "Edit an account."

    fields = GET_AccountEdit.fields

    def is_accessible(self):
        return self.is_login_admin() or self.is_login_account()

    def handle(self, resource, request, application):
        "Handle the request; perform actions according to the request."
        if self.is_login_admin():
            skip = set(['password'])
        else:
            skip = set()
        values = self.parse_fields(request, skip=skip)
        current = values.pop('password', '')
        if current:
            try:
                self.account.check_password(current)
            except ValueError:
                raise HTTP_FORBIDDEN('invalid current password')
        new = values.pop('new_password')
        confirm = values.pop('confirm_new_password', None)
        if new:
            if len(new) < configuration.MIN_PASSWORD_LENGTH:
                raise HTTP_BAD_REQUEST("password must be at least %s characters"
                                       % configuration.MIN_PASSWORD_LENGTH)
            if new != confirm:
                raise HTTP_BAD_REQUEST('password confirmation failed')
            self.account.password = new
        self.account.email = values.get('email', None)
        self.account.description = values.get('description', None)
        self.account.save()
        if self.is_login_admin():
            self.account.set_teams(values.get('teams', []))
        self.set_redirect(values.get('url', application.get_url('account',
                                                                self.account)))


class GET_AccountCreate(MethodMixin, GET):
    "The form to create a new account."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                FormHtmlRepresentation]

    fields = (StringField('name', title='Name',
                          required=True,
                          descr='Account name, which must be unique.'
                          ' May contain alphanumerical characters,'
                          ' dash (-), underscore (_) and dot (.)'),
              PasswordField('password', title='Password',
                            required=True,
                            descr="At least %s characters."
                            % configuration.MIN_PASSWORD_LENGTH),
              PasswordField('confirm_password',
                            title='Confirm password',
                            required=True),
              StringField('email', title='Email'),
              TextField('description', title='Description'),
              MultiSelectField('teams', title='Teams',
                               check=False,
                               descr='Indicate team memberships'
                               ' for the account.'))

    def is_accessible(self):
        return self.is_login_admin()

    def get_data_resource(self, resource, request, application):
        data = dict(title='Create account')
        fill = dict(teams=dict(options=[str(t) for t in self.db.get_teams()]))
        data['form'] = dict(fields=self.get_fields_data(fill=fill),
                            title='Enter data for new account',
                            label='Create',
                            href=resource.get_url(),
                            cancel=application.get_url('accounts'))
        return data


class POST_AccountCreate(MethodMixin, RedirectMixin, POST):
    "Create a new account."

    fields = GET_AccountCreate.fields

    def is_accessible(self):
        return self.is_login_admin()

    def handle(self, resource, request, application):
        "Handle the request; perform actions according to the request."
        values = self.parse_fields(request)
        values['name'] = values['name'].strip()
        if len(values['name']) <= 3:
            raise HTTP_BAD_REQUEST('account name is too short')
        allowed = string.letters + string.digits + '-_.'
        if set(values['name']).difference(allowed):
            raise HTTP_BAD_REQUEST('disallowed characters in account name')
        try:
            self.db.get_account(values['name'])
        except KeyError:
            pass
        else:
            raise HTTP_BAD_REQUEST("account name '%s' already in use" %
                                   values['name'])
        self.account = Account(self.db)
        self.account.name= values['name']
        password = values['password']
        if len(password) < configuration.MIN_PASSWORD_LENGTH:
            raise HTTP_BAD_REQUEST("password must be at least  %s characters"
                                   % configuration.MIN_PASSWORD_LENGTH)
        if password != values.pop('confirm_password'):
                raise HTTP_BAD_REQUEST('password confirmation failed')
        self.account.password = password
        self.account.email = values.get('email', None)
        self.account.description = values.get('description', None)
        self.account.save()
        self.account.set_teams(values.get('teams', []))
        self.set_redirect(application.get_url('account', self.account))
