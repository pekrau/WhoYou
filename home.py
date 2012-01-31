""" WhoYou: Simple accounts database for web applications.

Home page.
"""

from .method_mixin import *
from .representation import *


class GET_Home(MethodMixin, GET):
    "Produce the WhoYou home page."

    outreprs = (JsonRepresentation,
                TextRepresentation,
                HtmlRepresentation)

    def get_data(self, resource, request, application):
        "Return a dictionary containing the data for the response."
        data = self.get_data_basic(resource, request, application)
        data['title'] = "%s %s" % (application.name, application.version)
        try:
            data['descr'] = open(configuration.README_FILE).read()
        except IOError:
            data['descr'] = 'Simple accounts database for web applications.'
        return data
