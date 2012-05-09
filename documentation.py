""" WhoYou: Simple accounts database for web applications.

Produce the documentation for the web resource API by introspection.
"""

from wrapid.documentation import *

from .base import *


class ApiDocumentationHtmlRepresentation(ApiDocumentationHtmlMixin,
                                         HtmlRepresentation):
    "HTML representation class for the API documentation."
    pass


class GET_WhoYouApiDocumentation(MethodMixin, GET_ApiDocumentation):
    "Produce the documentation for the web resource API by introspection."

    outreprs = [JsonRepresentation,
                TextRepresentation,
                ApiDocumentationHtmlRepresentation]
