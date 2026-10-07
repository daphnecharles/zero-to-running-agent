# pgsnap

Point-in-time snapshots for PostgreSQL, built for developers who want to test migrations against real data without copying production.

pgsnap is an open source Python library and CLI. It takes copy-on-write snapshots of a PostgreSQL database in seconds, lets you run a migration or a data pipeline against the snapshot, and throws it away when you're done.

## Features

- Snapshot a 50 GB database in under ten seconds using filesystem clones
- Run migrations, ETL jobs or analytics queries against a disposable copy
- GitHub Actions integration for testing migrations in CI
- MIT licensed, with 40+ contributors

## Who it's for

Backend and data engineers who maintain PostgreSQL in production and want safer deploys.
