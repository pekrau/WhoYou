""" WhoYou: Simple accounts database for web applications.

Apache WSGI interface using the 'wrapid' package.
"""

import wrapid
from wrapid.application import Application
from wrapid.file import GET_File

import whoyou
from whoyou import configuration
from whoyou.home import *
from whoyou.account import *
from whoyou.team import *
from whoyou.documentation import *

# Package dependency
assert wrapid.__version__ == '12.4'


application = Application(name='WhoYou',
                          version=whoyou.__version__,
                          host=configuration.HOST,
                          debug=configuration.DEBUG)


# Home
application.add_resource('/',
                         name='Home',
                         GET=GET_Home)

# Static resources; accessed often, keep at beginning of the chain.
class GET_File_static(GET_File):
    dirpath       = configuration.STATIC_DIR
    cache_control = 'max-age=300'

application.add_resource('/static/{filename}',
                         name='File',
                         GET=GET_File_static)

# Account resources
application.add_resource('/accounts',
                         name='Account list',
                         GET=GET_Accounts)
application.add_resource('/account/{account}',
                         name='Account',
                         GET=GET_Account)
application.add_resource('/account/{account}/edit',
                         name='Account edit',
                         GET=GET_AccountEdit,
                         POST=POST_AccountEdit)
application.add_resource('/account',
                         name='Account create',
                         GET=GET_AccountCreate,
                         POST=POST_AccountCreate)

# Team resources
application.add_resource('/teams',
                         name='Team list',
                         GET=GET_Teams)
application.add_resource('/team/{team}',
                         name='Team',
                         GET=GET_Team)
application.add_resource('/team/{team}/edit',
                         name='Team edit',
                         GET=GET_TeamEdit,
                         POST=POST_TeamEdit)
application.add_resource('/team',
                         name='Team create',
                         GET=GET_TeamCreate,
                         POST=POST_TeamCreate)

# Documentation resources
application.add_resource('/doc',
                         name='Documentation API',
                         GET=GET_WhoYouApiDocumentation)
