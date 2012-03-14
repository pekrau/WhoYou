WhoYou: Simple accounts database for web applications
-----------------------------------------------------

The WhoYou system is a database for accounts and teams.
An account can be a member of any number of teams.

The database can be viewed and edited via a RESTful web interface.

A simple Python API is provided for server-side account authorization
and data retrieval. This can be used for other web applications on
the server.

### Implementation

The account passwords are stored as hashes using a salt which must
be set at installation time.

The system is written in Python 2.6; 2.7 should also work.

- [https://github.com/pekrau/whoyou](https://github.com/pekrau/whoyou):
  Source code for the WhoYou system.
- [https://github.com/pekrau/wrapid](https://github.com/pekrau/wrapid):
  Package **wrapid** providing the web service framework.
- [https://github.com/pekrau/hypertext](https://github.com/pekrau/hypertext):
  Package **HyperText** for producing the HTML of the web service interface.

The **Sqlite3** database system is used as storage back-end in the current
implementation. It is included in the standard Python distribution.
