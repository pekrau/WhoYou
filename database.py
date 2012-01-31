""" WhoYou: Simple accounts database for web applications.

Interface to the database.
"""

import sqlite3
import json

from wrapid.utils import rstr

from whoyou import configuration


class Database(object):
    "Interface to the WhoYou database."

    def __init__(self, path=configuration.MASTER_DB_FILE):
        self.path = path

    def open(self):
        assert not self.opened
        self.cnx = sqlite3.connect(self.path)
        self.cnx.text_factory = str
        self.account_cache = dict()
        self.team_cache = dict()

    def close(self):
        try:
            self.cnx.close()
        except AttributeError:
            pass
        else:
            del self.cnx

    @property
    def opened(self):
        return hasattr(self, 'cnx')

    def execute(self, sql, *values):
        assert self.opened
        cursor = self.cnx.cursor()
        cursor.execute(sql, values)
        return cursor

    def commit(self):
        assert self.opened
        self.cnx.commit()

    def create_account(self, name, password=None, description=None):
        try:
            self.get_account(name)
        except KeyError:
            pass
        else:
            raise ValueError("account '%s' already exists", name)
        account = Account(self)
        account.name = name
        if password:
            account.password = configuration.get_password_hexdigest(password)
        account.description = description
        account.save()
        return account

    def get_accounts(self):
        "Return list of all accounts."
        assert self.opened
        cursor = self.execute('SELECT name FROM account ORDER BY name')
        result = []
        for record in cursor:
            result.append(self.get_account(record[0]))
        return result

    def get_account(self, name, password=None):
        """Return the Account instance.
        If the password is given, then authenticate.
        Raise KeyError if no such account.
        Raise ValueError if incorrect password.
        """
        assert self.opened
        try:
            account = self.account_cache[name]
        except KeyError:
            account = Account(self, name=name)
            self.account_cache[account.name] = account
        if password:
            account.check_password(password)
        return account

    def get_account_data(self, name, password=None):
        """Return the data dictionary for the given user account.
        If the password is given, then authenticate.
        Raise KeyError if no such account.
        Raise ValueError if incorrect password.
        """
        return self.get_account(name, password=password).get_data()

    def create_team(self, name, description=None):
        try:
            self.get_team(name)
        except KeyError:
            pass
        else:
            raise ValueError("team '%s' already exists", name)
        team = Team(self)
        team.name = name
        team.description = description
        team.save()
        return team

    def get_teams(self):
        "Return list of all teams."
        assert self.opened
        cursor = self.execute('SELECT name FROM team ORDER BY name')
        result = []
        for record in cursor:
            result.append(self.get_team(record[0]))
        return result

    def get_team(self, name):
        """Return the Team instance for the name.
        Raise KeyError if no such team.
        """
        assert self.opened
        try:
            return self.team_cache[name]
        except KeyError:
            team = Team(self, name=name)
            self.team_cache[team.name] = team
            return team

    def get_team_data(self, name):
        """Return the data dictionary for the given team.
        Raise KeyError if no such account.
        """
        return self.get_team(name).get_data()

    def save(self, item):
        "Save the instance (Account or Team)."
        item.save(self)

    def create(self):
        assert self.opened
        self.execute('CREATE TABLE account'
                     '(id INTEGER PRIMARY KEY,'
                     ' name TEXT UNIQUE NOT NULL,'
                     ' password TEXT,'
                     ' email TEXT,'
                     ' description TEXT,'
                     ' properties TEXT)')
        self.execute('CREATE TABLE team'
                     '(id INTEGER PRIMARY KEY,'
                     ' name TEXT UNIQUE NOT NULL,'
                     ' description TEXT,'
                     ' properties TEXT)')
        self.execute('CREATE TABLE account_team'
                     '(account INTEGER NOT NULL REFERENCES account(id)'
                     '  ON DELETE RESTRICT,'
                     ' team INTEGER NOT NULL REFERENCES team(id)'
                     '  ON DELETE RESTRICT,'
                     ' admin INTEGER,'
                     ' UNIQUE (account, team))')


class Account(object):
    "User account."

    def __init__(self, db, name=None):
        self.db = db
        if name:
            self.fetch(name)
        else:
            self.id = None
            self.name = None
            self.password = None
            self.description = None
            self.email = None
            self.properties = dict()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Account '%s'" % self.name

    def fetch(self, name):
        "Raise KeyError if no such account."
        cursor = self.db.execute('SELECT id,password,description,email,'
                                 ' properties FROM account WHERE name=?',
                                  name)
        record = cursor.fetchone()
        if not record:
            raise KeyError("no such Account '%s'" % name)
        self.id = record[0]
        self.name = str(name)
        self.password = record[1]
        self.description = record[2]
        self.email = record[3]
        self.properties = rstr(json.loads(record[4]))

    def save(self):
        """It is assumed that the password has already been
        converted to its hash hex digest using the salt.
        """
        assert self.name
        assert len(self.name.split()) == 1
        cursor = self.db.execute('SELECT id FROM account WHERE name=?',
                                 self.name)
        record = cursor.fetchone()
        if record:
            if record[0] != self.id:
                raise ValueError("id mismatch for Account '%s'" % self.name)
            self.db.execute('UPDATE account SET password=?,description=?,'
                            ' email=?,properties=? WHERE id=?',
                            self.password,
                            self.description,
                            self.email,
                            json.dumps(self.properties),
                            self.id)
        else:
            cursor = self.db.execute('INSERT INTO account'
                                     ' (name,password,description,'
                                     '  email,properties)'
                                     ' VALUES(?,?,?,?,?)',
                                     self.name,
                                     self.password,
                                     self.description,
                                     self.email,
                                     json.dumps(self.properties))
            self.id = cursor.lastrowid
        self.db.commit()

    def get_data(self):
        "Return the account data in a dictionary."
        return dict(name=str(self.name),
                    teams=[str(t) for t in self.get_teams()],
                    description=self.description,
                    email=self.email,
                    properties=self.properties)

    def get_teams(self):
        "Return all teams this account is a member of."
        assert self.id
        cursor = self.db.execute('SELECT t.name'
                                 ' FROM team AS t, account_team AS at'
                                 ' WHERE t.id=at.team AND at.account=?'
                                 ' ORDER BY t.name',
                                 self.id)
        result = []
        for record in cursor.fetchall():
            result.append(self.db.get_team(record[0]))
        return result

    def set_teams(self, teamnames):
        """Set the account's teams to the ones named in the given list.
        Remove from those teams not mentioned.
        Add to those mentioned, and not already member of.
        """
        current = set([str(t) for t in self.get_teams()])
        new = set(teamnames)
        for name in current.difference(new):
            try:
                team = self.db.get_team(name)
            except KeyError:
                pass
            else:
                team.remove_member(self)
        for name in new.difference(current):
            try:
                team = self.db.get_team(name)
            except KeyError:
                pass
            else:
                team.add_member(self)
        self.db.commit()

    def check_password(self, password):
        """Raise ValueError if the password does not match.
        The incoming password must be in the clear;
        it has *not* been converted to the hash hex digest."""
        if self.password:
            if configuration.get_password_hexdigest(password) != self.password:
                raise ValueError('incorrect password')


class Team(object):
    "User account team."

    def __init__(self, db, name=None):
        self.db = db
        if name:
            self.fetch(name)
        else:
            self.id = None
            self.name = None
            self.description = None
            self.properties = dict()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Team '%s'" % self.name

    def fetch(self, name):
        "Raise KeyError if no such team."
        cursor = self.db.execute('SELECT id,description,properties'
                                 ' FROM team WHERE name=?',
                                 name)
        record = cursor.fetchone()
        if not record:
            raise KeyError("no such Team '%s'" % name)
        self.id = record[0]
        self.name = str(name)
        self.description = record[1]
        self.properties = rstr(json.loads(record[2]))

    def save(self):
        assert self.name
        assert len(self.name.split()) == 1
        cursor = self.db.execute('SELECT id FROM team WHERE name=?', self.name)
        record = cursor.fetchone()
        if record:
            if record[0] != self.id:
                raise ValueError("id mismatch for Team '%s'" % self.name)
            self.db.execute('UPDATE team SET description=?,properties=?'
                            ' WHERE id=?',
                            self.description,
                            json.dumps(self.properties),
                            self.id)
        else:
            cursor = self.db.execute('INSERT INTO team'
                                     ' (name,description,properties)'
                                     ' VALUES(?,?,?)',
                                     self.name,
                                     self.description,
                                     json.dumps(self.properties))
            self.id = cursor.lastrowid
        self.db.commit()

    def get_data(self):
        "Return the team data in a dictionary."
        return dict(name=self.name,
                    members=[str(m) for m in self.get_members()],
                    admins=[str(m) for m in self.get_admins()],
                    description=self.description,
                    properties=self.properties)

    def get_members(self):
        "Return all accounts being members of this team."
        assert self.id
        cursor = self.db.execute('SELECT a.name'
                                 ' FROM account AS a, account_team AS at'
                                 ' WHERE a.id=at.account AND at.team=?',
                                 self.id)
        return [self.db.get_account(record[0]) for record in cursor]

    def get_admins(self):
        "Return all accounts being admin members of this team."
        assert self.id
        cursor = self.db.execute('SELECT a.name'
                                 ' FROM account AS a, account_team AS at'
                                 ' WHERE a.id=at.account AND at.team=?'
                                 ' AND at.admin=1',
                                 self.id)
        return [self.db.get_account(record[0]) for record in cursor]

    def add_member(self, account, admin=False):
        assert self.id
        assert isinstance(account, Account)
        assert account.id
        if self.is_member(account): return
        self.db.execute('INSERT INTO account_team (account, team, admin)'
                        ' VALUES(?,?,?)',
                        account.id,
                        self.id,
                        int(bool(admin)))

    def remove_member(self, account):
        assert self.id
        assert isinstance(account, Account)
        assert account.id
        if not self.is_member(account): return
        self.db.execute('DELETE FROM account_team WHERE account=? AND team=?',
                        account.id,
                        self.id)

    def set_admin(self, account, admin=True):
        assert self.id
        assert isinstance(account, Account)
        assert account.id
        assert self.is_member(account)
        self.db.execute('UPDATE account_team SET admin=?'
                        ' WHERE account=? AND team=?',
                        int(bool(admin)),
                        account.id,
                        self.id)

    def set_admins(self, accountnames):
        """Set the team's administrators to the ones named in the given list.
        Remove administrators not mentioned.
        Add administrators mentioned, and not already set.
        """
        current = set([str(a) for a in self.get_admins()])
        new = set(accountnames)
        for name in current.difference(new):
            try:
                account = self.db.get_account(name)
            except KeyError:
                pass
            else:
                self.set_admin(account, admin=False)
        for name in new.difference(current):
            try:
                account = self.db.get_account(name)
            except KeyError:
                pass
            else:
                self.set_admin(account, admin=True)
        self.db.commit()

    def is_member(self, account):
        "Is the given account a member of this team?"
        assert self.id
        assert isinstance(account, Account)
        assert account.id
        cursor = self.db.execute('SELECT COUNT(*) FROM account_team'
                                 ' WHERE account_team.account=?'
                                 '   AND account_team.team=?',
                                 account.id,
                                 self.id)
        return bool(cursor.fetchone()[0])

    def is_admin(self, account):
        "Is the given account an admin member of this team?"
        assert self.id
        assert isinstance(account, Account)
        assert account.id
        cursor = self.db.execute('SELECT COUNT(*) FROM account_team'
                                 ' WHERE account_team.account=?'
                                 '   AND account_team.team=?'
                                 ' AND account_team.admin=1',
                                 account.id,
                                 self.id)
        return bool(cursor.fetchone()[0])


if __name__ == '__main__':
    import os.path
    import getpass

    db = Database()
    if os.path.exists(configuration.MASTER_DB_FILE):
        db.open()
        print 'WhoYou database exists.'
    else:
        db.open()
        db.create()
        print 'Created WhoYou database.'
        password = getpass.getpass("Give password for 'admin' account > ")
        admin = db.create_account('admin',
                                  password=password,
                                  description='Site administrator.')
        team = db.create_team('admin',
                              description='Accounts with admin privileges.')
        team.add_member(admin, admin=True)
        db.create_account('anonymous',
                          description='Anonymous user without password.')
        try:
            from whoyou import tests
        except ImportError:
            pass
        else:
            db.create_account(tests.ACCOUNT,
                              password=tests.PASSWORD,
                              description='Test account.')
    print 'Accounts:'
    for a in db.get_accounts():
        print a.get_data()
    print 'Teams:'
    for t in db.get_teams():
        print t.get_data()
    db.close()
