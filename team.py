""" WhoYou: Simple accounts database for web applications.

Team resources.
"""

import logging
import string

from .database import Account
from .method_mixin import *
from .representation import *


class TeamsHtmlRepresentation(HtmlRepresentation):
    "HTML representation of the teams list."

    def get_content(self):
        rows = [TR(TH('Name'),
                   TH('Administrators'),
                   TH('Members'))]
        for team in self.data['teams']:
            administrators = []
            members = []
            for account in team['members']:
                name = "%(name)s" % account
                if account['is_admin']:
                    administrators.append(str(A(name, href=account['href'])))
                else:
                    members.append(str(A(name, href=account['href'])))
            rows.append(TR(TD(A(team['name'], href=team['href'])),
                           TD(', '.join(administrators)),
                           TD(', '.join(members))))
        return TABLE(klass='list', *rows)


class GET_Teams(MethodMixin, GET):
    "Return the teams list."

    outreprs = (JsonRepresentation,
                TextRepresentation,
                TeamsHtmlRepresentation)

    def is_access(self):
        return self.is_admin()

    def get_data(self, resource, request, application):
        self.allow_admin()
        data = self.get_data_basic(resource, request, application)
        data['title'] = 'Teams'
        data['teams'] = []
        for team in self.db.get_teams():
            teamdata = team.get_data()
            teamdata['href'] = application.get_url('team', team)
            teamdata['members'] = []
            for account in team.get_members():
                accountdata = dict(name=str(account),
                                   href=application.get_url('account', account),
                                   is_admin=team.is_admin(account))
                teamdata['members'].append(accountdata)
            data['teams'].append(teamdata)
        data['operations'] = [dict(title='Create team',
                                   href=application.get_url('team'))]
        return data


class TeamHtmlRepresentation(HtmlRepresentation):
    "HTML representation of the team data."

    def get_content(self):
        team = self.data['team']
        administrators = []
        members = []
        for account in team['members']:
            name = account['name']
            if account['is_admin']:
                administrators.append(str(A(name, href=account['href'])))
            else:
                members.append(str(A(name, href=account['href'])))
        table = TABLE(klass='input')
        table.append(TR(TH('Administrators'),
                        TD(' '.join(administrators))))
        table.append(TR(TH('Members'),
                        TD(' '.join(members))))
        table.append(TR(TH('Description'),
                        TD(markdown_to_html(team.get('description')))))
        return table


class GET_Team(MethodMixin, GET):
    "Return the team data."

    outreprs = (JsonRepresentation,
                TextRepresentation,
                TeamHtmlRepresentation)

    def is_access(self):
        return self.is_admin() or self.team.is_member(self.login)

    def get_data(self, resource, request, application):
        self.team = self.get_team(resource.variables)
        if not self.team:
            raise HTTP_NOT_FOUND
        self.allow_access()
        data = self.get_data_basic(resource, request, application)
        data['title'] = "Team %s" % self.team
        data['team'] = self.team.get_data()
        members = []
        for name in data['team'].pop('members'):
            is_admin = self.team.is_admin(self.db.get_account(name))
            members.append(dict(name=name,
                                href=application.get_url('account', name),
                                is_admin=is_admin))
        data['team']['members'] = members
        url = application.get_url('team', self.team.name, 'edit')
        data['operations'] = [dict(title='Edit team',
                                   href=url)]
        return data


class GET_TeamCreate(MethodMixin, GET):
    "Return the create form for a new team."

    outreprs = (JsonRepresentation,
                TextRepresentation,
                FormHtmlRepresentation)

    fields = (StringField('name', title='Name',
                          required=True,
                          descr='Team name, which must be unique.'
                          ' May contain alphanumerical characters,'
                          ' dash (-), underscore (_) and dot (.)'),
              TextField('description', title='Description'))

    def is_access(self):
        return self.is_admin()

    def get_data(self, resource, request, application):
        data = self.get_data_basic(resource, request, application)
        data['title'] = 'Create team'
        data['form'] = dict(fields=self.get_fields_data(),
                            title='Enter data for new team',
                            href=resource.get_url(),
                            cancel=application.get_url('teams'))
        return data
        

class POST_TeamCreate(MethodMixin, POST):
    """Perform the team creation.
    The response is a HTTP 303 'See Other' redirection to the team resource.
    There is no output representation for this resource and method.
    """

    fields = GET_TeamCreate.fields

    def is_access(self):
        return self.is_admin()

    def handle(self, resource, request, application):
        "Handle the request; perform actions according to the request."
        self.allow_access()
        values = self.parse_fields(request)
        values['name'] = values['name'].strip()
        if len(values['name']) <= 3:
            raise HTTP_BAD_REQUEST('team name is too short')
        allowed = string.letters + string.digits + '-_.'
        if set(values['name']).difference(allowed):
            raise HTTP_BAD_REQUEST('team name contains disallowed characters')
        try:
            self.db.get_team(values['name'])
        except KeyError:
            pass
        else:
            raise HTTP_BAD_REQUEST("team name '%s' already in use" %
                                   values['name'])
        self.team = Team(self.db)
        self.team.name= values['name']
        self.team.description = values.get('description', None)
        self.team.save()

    def get_response(self, resource, request, application):
        return HTTP_SEE_OTHER(Location=application.get_url('team', self.team))


class GET_TeamEdit(MethodMixin, GET):
    "Return the edit form for an team."

    outreprs = (JsonRepresentation,
                TextRepresentation,
                FormHtmlRepresentation)

    fields = (TextField('description', title='Description'),
              MultiSelectField('administrators', title='Administrators',
                               check=False,
                               descr='Check the members to be'
                               ' administrators of this group.'))

    def is_access(self):
        return self.is_admin() or self.team.is_admin(self.login)

    def get_data(self, resource, request, application):
        team = self.get_team(resource.variables)
        if not team:
            raise HTTP_NOT_FOUND
        self.allow_access()
        data = self.get_data_basic(resource, request, application)
        data['title'] = "Edit team %s" % team
        values = dict(description=team.description)
        fill = dict(administrators=dict(options=[str(m)
                                                 for m in team.get_members()]))
        default = dict(administrators=[str(a) for a in team.get_admins()])
        data['form'] = dict(fields=self.get_fields_data(fill=fill,
                                                        default=default),
                            values=values,
                            title='Modify team data',
                            href=resource.get_url(),
                            cancel=application.get_url('team', team))
        return data


class POST_TeamEdit(MethodMixin, POST):
    """Perform the edit on an team.
    The response is a HTTP 303 'See Other' redirection to the team resource.
    There is no output representation for this resource and method.
    """

    fields = GET_TeamEdit.fields

    def is_access(self):
        return self.is_admin() or self.team.is_admin(self.login)

    def handle(self, resource, request, application):
        "Handle the request; perform actions according to the request."
        self.team = self.get_team(resource.variables)
        if not self.team:
            raise HTTP_NOT_FOUND
        self.allow_access()
        values = self.parse_fields(request)
        self.team.description = values.get('description', None)
        self.team.save()
        self.team.set_admins(values.get('administrators', []))

    def get_response(self, resource, request, application):
        return HTTP_SEE_OTHER(Location=application.get_url('team', self.team))
