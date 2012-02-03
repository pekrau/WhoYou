""" WhoYou: Simple accounts database for web applications.

Apache WSGI interface using the 'wrapid' package.
"""

import wrapid
from wrapid.resource import Resource
from wrapid.application import Application
from wrapid.get_static import GET_Static
from wrapid.get_documentation import GET_Documentation

import whoyou
from whoyou import configuration
from whoyou.home import *
from whoyou.account import *
from whoyou.team import *

# Package dependency
assert wrapid.__version__ == '2.0'


class WhoYou(Application):
    version = whoyou.__version__
    debug   = configuration.DEBUG

application = WhoYou()

# Home
application.append(Resource('/',
                            type='Home',
                            GET=GET_Home(),
                            descr='WhoYou home page.'))

# Static resources; accessed often, keep at beginning of the chain.
application.append(Resource('/static/{filename}',
                            type='File',
                            GET=GET_Static(configuration.STATIC_DIR,
                                           cache_control='max-age=3600')))

# Account resources
application.append(Resource('/accounts',
                            type='Account list',
                            GET=GET_Accounts()))
application.append(Resource('/account/{account}',
                            type='Account',
                            GET=GET_Account()))
application.append(Resource('/account/{account}/edit',
                            type='Account edit',
                            GET=GET_AccountEdit(),
                            POST=POST_AccountEdit()))
application.append(Resource('/account',
                            type='Account create',
                            GET=GET_AccountCreate(),
                            POST=POST_AccountCreate()))

# Team resources
application.append(Resource('/teams',
                            type='Team list',
                            GET=GET_Teams()))
application.append(Resource('/team/{team}',
                            type='Team',
                            GET=GET_Team()))
application.append(Resource('/team/{team}/edit',
                            type='Team edit',
                            GET=GET_TeamEdit(),
                            POST=POST_TeamEdit()))
application.append(Resource('/team',
                            type='Team create',
                            GET=GET_TeamCreate(),
                            POST=POST_TeamCreate()))

# Other resources
application.append(Resource('/doc',
                            type='Documentation API',
                            GET=GET_Documentation()))