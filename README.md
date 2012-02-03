WhoYou: Simple accounts database for web applications
-----------------------------------------------------

The WhoYou system is a database for accounts and teams.
An account can be a member of any number of teams.

The account passwords are stored as hashes using a salt which must
be set at installation time.

The database is viewed and edited via a RESTful web interface.

A simple Python API is provided to account authorization and data retrieval.
This can be used for other web applications on the same server.

### Implementation

The Sqlite3 database system is used as storage back-end in the current
implementation.

The WhoYou source code lives at
[https://github.com/pekrau/whoyou](https://github.com/pekrau/whoyou).
It relies on the packages **wrapid** at
[https://github.com/pekrau/wrapid](https://github.com/pekrau/wrapid)
and **HyperText** at
[https://github.com/pekrau/HyperText](https://github.com/pekrau/HyperText).
