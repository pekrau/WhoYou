""" WhoYou: Simple accounts database for web applications.

General representation classes.
"""

import urllib

from wrapid.html_representation import *
from wrapid.json_representation import JsonRepresentation
from wrapid.text_representation import TextRepresentation


class HtmlRepresentation(BaseHtmlRepresentation):
    "HTML representation of the resource."

    def get_url(self, *segments, **query):
        "Return a URL based on the application URL."
        url = '/'.join([self.data['application']['href']] + list(segments))
        if query:
            url += '?' + urllib.urlencode(query)
        return url

    def get_head(self):
        head = super(HtmlRepresentation, self).get_head()
        head.append(LINK(rel='stylesheet',
                         href=self.get_url('static', 'style.css'),
                         type='text/css'))
        return head

    def get_logo(self):
        return A(IMG(src=self.get_url('static', 'whoyou.png'),
                     width=84, height=80,
                     alt=self.data['application']['name'],
                     title=self.data['application']['name']),
                 href=self.data['application']['href'])

    def get_login(self):
        loginname = self.data.get('loginname')
        if loginname and loginname != 'anonymous':
            url = self.get_url('account', loginname)
            return DIV("Logged in as: %s" % A(loginname, href=url),
                       style='white-space: nowrap;')
        else:
            return TABLE(TR(TD(I('not logged in')),
                            TD(FORM(INPUT(type='submit', value='Login'),
                                    method='GET',
                                    action=self.get_url('login')))),
                         style='white-space: nowrap;')


class FormHtmlRepresentation(HtmlRepresentation):
    "HTML representation of the form page for data input."

    submit = 'Save'

    def get_content(self):
        data = self.data['form']
        required = IMG(src=self.get_url('static', 'required.png'))
        form = self.get_form(data['fields'],
                             data['href'],
                             values=data.get('values', dict()),
                             required=required,
                             legend=data['title'],
                             klass='input',
                             submit=self.submit)
        return DIV(P(form),
                   P(FORM(INPUT(type='submit', value='Cancel'),
                          method='GET',
                          action=data.get('cancel') or data['href'])))
