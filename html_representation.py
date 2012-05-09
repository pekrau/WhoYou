""" WhoYou: Simple accounts database for web applications.

General HTML representation classes.
"""

from wrapid.html_representation import *


class HtmlRepresentation(BaseHtmlRepresentation):
    "HTML representation of the resource."

    logo        = 'static/whoyou.png'
    stylesheets = ['static/standard.css']

    def get_icon(self, name):
        return IMG(src=self.get_url('static', "%s.png" % name),
                   alt=name, title=name, width=16, height=16)


class FormHtmlRepresentation(FormHtmlMixin, HtmlRepresentation):
    "HTML representation of the form page for data input."
    pass
