# Security policy

## Supported versions

Fixes go into the latest release on [PyPI](https://pypi.org/project/sqlite2duckdb/).
There are no maintained older branches.

## Reporting a vulnerability

Report privately rather than in a public issue, through
[GitHub's private vulnerability reporting](https://github.com/dridk/sqlite2duckdb/security/advisories/new)
or by email to sacha.schutz@pm.me. Expect an acknowledgement within a week.

Useful in a report: the sqlite database or the schema that triggers it, the version of
sqlite2duckdb and of duckdb, and what an attacker would gain.

## Scope

sqlite2duckdb reads a sqlite file and writes a duckdb file. Both are handed to it by
whoever runs it, and the DDL read from the source database is replayed against duckdb.
So a sqlite file from an untrusted source should be treated as untrusted input, in the
same way you would treat one before opening it with any other tool.
