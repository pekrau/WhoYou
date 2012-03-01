""" WhoYou: Simple accounts database for web applications.

The functions defined here are to be used by other web applications.
"""

from .database import Database


def get_db():
    db = Database()
    db.open()
    return db

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
    return get_db().get_account(name, password=password).get_data()

def get_accounts():
    "Return a list of all accounts as dictionaries."
    return [a.get_data() for a in get_db().get_accounts()]

def get_team(name):
    """Get the team data dictionary containing items:
    Raise KeyError if no such team.
    - name: str
    - members: list of str
    - admins: list of str
    - description: str or None
    - properties: dict
    """
    return get_db().get_team(name).get_data()

def update_account_properties(name, applicationname, properties):
    "Update the properties of the given account for the given application."
    account = get_db().get_account(name)
    account.properties.setdefault(applicationname, dict()).update(properties)
    account.save()
