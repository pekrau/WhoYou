""" WhoYou: Simple accounts database for web applications.

Home page.
"""

from .base import *


class Home(MethodMixin, GET):
    "The WhoYou home page."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                HtmlRepresentation]

    def get_data_resource(self, request):
        "Return the dictionary with the resource-specific response data."
        return dict(resource='Home',
                    descr=open(configuration.README_FILE).read())
