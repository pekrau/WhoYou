""" WhoYou: Simple accounts database for web applications.

The methods defined here are to be used by other web applications.
"""

__version__ = '0.3'


def get_account(name, password=None):
    """Get the account data dictionary containing items:
    Raise KeyError if no such account.
    Raise ValueError if incorrect password.
    - name: str
    - teams: list of str
    - description: str or None
    - email: str or None
    - properties: dict
    If the password is given, then authenticate.
    Raise KeyError if no such account.
    Raise ValueError if incorrect password.
    """
    from .database import Database
    db = Database()
    db.open()
    return db.get_account_data(name, password=password)

def get_team(name):
    """Get the team data dictionary containing items:
    Raise KeyError if no such team.
    - name: str
    - members: list of str
    - admins: list of str
    - description: str or None
    - properties: dict
    """
    from .database import Database
    db = Database()
    db.open()
    return db.get_team_data(name)
