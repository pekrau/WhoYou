""" WhoYou: Simple accounts database for web applications.

Team resources.
"""

import string

from .base import *
from .database import Account


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
    "The list of teams."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                TeamsHtmlRepresentation]

    def is_accessible(self):
        return self.is_login_admin()

    def get_data_operations(self, request):
        "Return the operations response data."
        return [dict(title='Create team',
                     href=request.application.get_url('team'))]

    def get_data_resource(self, request):
        "Return the dictionary with the resource-specific response data."
        data = dict(title='Teams')
        data['teams'] = []
        get_url = request.application.get_url
        for team in self.db.get_teams():
            teamdata = team.get_data()
            teamdata['href'] = get_url('team', team)
            teamdata['members'] = []
            for account in team.get_members():
                accountdata = dict(name=str(account),
                                   href=get_url('account', account),
                                   is_admin=team.is_admin(account))
                teamdata['members'].append(accountdata)
            data['teams'].append(teamdata)
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
                        TD(self.to_html(team.get('description')))))
        return table


class TeamMixin(object):
    "Mixin class to set the team to operate on."

    def set_current(self, request):
        """Set the team to operate on.
        This handles the case where a team name contains a dot
        and a short (<=4 chars) last name, which will otherwise
        be confused for a FORMAT specification.
        """
        try:
            self.team = Team(self.db, request.variables['team'])
        except KeyError:
            if not request.variables.get('FORMAT'):
                raise HTTP_NOT_FOUND
            name = request.variables['team'] + request.variables['FORMAT']
            try:
                self.team = Team(self.db, name)
            except KeyError:
                raise HTTP_NOT_FOUND
            request.undo_format_specifier('team')

    def is_login_member(self):
        "Is the login account member of the team to operate on?"
        return self.team.is_member(self.db.get_account(self.login['name']))


class GET_Team(TeamMixin, MethodMixin, GET):
    "Data for a team."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                TeamHtmlRepresentation]

    def is_accessible(self):
        return self.is_login_admin() or self.is_login_member()

    def get_data_operations(self, request):
        "Return the operations response data."
        url = request.application.get_url('team', self.team.name, 'edit')
        return [dict(title='Edit team', href=url)]

    def get_data_resource(self, request):
        "Return the dictionary with the resource-specific response data."
        data = dict(title="Team %s" % self.team)
        data['team'] = self.team.get_data()
        members = []
        for name in data['team'].pop('members'):
            url = request.application.get_url('account', name)
            is_admin = self.team.is_admin(self.db.get_account(name))
            members.append(dict(name=name,
                                href=url,
                                is_admin=is_admin))
        data['team']['members'] = members
        return data


class GET_TeamEdit(TeamMixin, MethodMixin, GET):
    "Edit a team."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                FormHtmlRepresentation]

    fields = (TextField('description', title='Description',
                        descr=' In [Markdown](http://daringfireball.net/'
                        'projects/markdown/) format.'),
              MultiSelectField('administrators', title='Administrators',
                               check=False,
                               descr='Check the members to be'
                               ' administrators of this group.'))

    def is_accessible(self):
        return self.is_login_admin() or self.is_login_member()

    def get_data_resource(self, request):
        "Return the dictionary with the resource-specific response data."
        data = dict(title="Edit team %s" % self.team)
        override = dict(administrators=dict(options=[str(m) for m in
                                                     self.team.get_members()],
                                            default=[str(a) for a in
                                                     self.team.get_admins()]))
        cancel = request.application.get_url('team', self.team)
        data['form'] = dict(fields=self.get_data_fields(override=override),
                            values=dict(description=self.team.description),
                            label='Save',
                            title='Modify team data',
                            href=request.get_url(),
                            cancel=cancel)
        return data


class POST_TeamEdit(TeamMixin, MethodMixin, RedirectMixin, POST):
    "Edit a team."

    fields = GET_TeamEdit.fields

    def is_accessible(self):
        return self.is_login_admin() or self.is_login_member()

    def process(self, request):
        "Handle the request; perform actions according to the request."
        values = self.parse_fields(request)
        self.team.description = values.get('description', None)
        self.team.save()
        self.team.set_admins(values.get('administrators', []))
        self.set_redirect(request.application.get_url('team', self.team))


class GET_TeamCreate(MethodMixin, GET):
    "The form to create a new team."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                FormHtmlRepresentation]

    fields = (StringField('name', title='Name',
                          required=True,
                          descr='Team name, which must be unique.'
                          ' May contain alphanumerical characters,'
                          ' dash (-), underscore (_) and dot (.)'),
              TextField('description', title='Description'))

    def is_accessible(self):
        return self.is_login_admin()

    def get_data_resource(self, request):
        "Return the dictionary with the resource-specific response data."
        data = dict(title='Create team')
        data['form'] = dict(fields=self.get_data_fields(),
                            title='Enter data for new team',
                            label='Create',
                            href=request.get_url(),
                            cancel=request.application.get_url('teams'))
        return data
        

class POST_TeamCreate(MethodMixin, RedirectMixin, POST):
    "Create a new team."

    fields = GET_TeamCreate.fields

    def is_accessible(self):
        return self.is_login_admin()

    def process(self, request):
        "Handle the request; perform actions according to the request."
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
        self.set_redirect(request.application.get_url('team', self.team))
