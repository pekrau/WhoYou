WhoYou: Simple accounts database for web applications
-----------------------------------------------------

The WhoYou system is a database for accounts and teams.
An account can be a member of any number of teams.

The account passwords are stored as hashes using a salt to be
defined upon installation.

The database is viewed and edited via a RESTful web interface.

A simple Python API is provided to support account and team data retrieval,
and account authorization, which can be used for other web applications
on the same server.
