""" WhoYou: Simple accounts database for web applications.

General representation classes.
"""

from wrapid.html_representation import *
from wrapid.json_representation import JsonRepresentation
from wrapid.text_representation import TextRepresentation


class HtmlRepresentation(BaseHtmlRepresentation):
    "HTML representation of the resource."

    logo        = 'static/whoyou.png'
    stylesheets = ['static/standard.css']

    def get_login(self):
        "Always logged in for all resources."
        login = self.data['login']
        return DIV('Logged in as: ',
                   A(login, href=self.get_url('account', login)))

    def get_icon(self, name):
        return IMG(src=self.get_url('static', "%s.png" % name),
                   alt=name, title=name, width=16, height=16)


class FormHtmlRepresentation(FormHtmlMixin, HtmlRepresentation):
    "HTML representation of the form page for data input."
    pass
