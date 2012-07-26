""" WhoYou: Simple accounts database for web applications.

Home page.
"""

import os

from .base import *


class Home(MethodMixin, GET):
    "The WhoYou home page."

    outreprs = [JsonRepresentation,
                HtmlRepresentation]

    def get_data_resource(self, request):
        "Return the dictionary with the resource-specific response data."
        try:
            dirpath = os.path.dirname(__file__)
            descr = open(os.path.join(dirpath, 'README.md')).read()
        except IOError:
            return dict(descr='Error: Could not find the README.rd file.',
                        resource='Home')
        else:
            descr = descr.split('\n')
            return dict(title=descr[0],
                        resource='Home',
                        descr='\n'.join(descr[3:]))
