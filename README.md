# redacty

[![Release](https://img.shields.io/github/v/release/wet-bulb/redacty)](https://img.shields.io/github/v/release/wet-bulb/redacty)
[![Build status](https://img.shields.io/github/actions/workflow/status/wet-bulb/redacty/main.yml?branch=main)](https://github.com/wet-bulb/redacty/actions/workflows/main.yml?query=branch%3Amain)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/redacty)](https://pypi.org/project/redacty/)
[![codecov](https://codecov.io/gh/wet-bulb/redacty/branch/main/graph/badge.svg)](https://codecov.io/gh/wet-bulb/redacty)
[![Commit activity](https://img.shields.io/github/commit-activity/m/wet-bulb/redacty)](https://img.shields.io/github/commit-activity/m/wet-bulb/redacty)
[![License](https://img.shields.io/github/license/wet-bulb/redacty)](https://img.shields.io/github/license/wet-bulb/redacty)

This is a CLI tool and Python API that redacts emails from bodies of text in a PostgreSQL database, with optional flags for an excluded domain and an older than x days filter.

- **Github repository**: <https://github.com/wet-bulb/redacty/>


## Installation

Install `redacty` with pip

```bash
  pip install redacty
```
    
## Usage/Examples
### Command-Line Interface (CLI)

``` bash
redacty <database_url> <table> <column> [-a AGE] [-x EXCLUDE]
```

- database_url: PostgreSQL database URL.
- table: Name of the table that holds the column to redact.
- column: Name of the column that holds the text to redact.

Optional arguments:

- -a AGE, --age AGE: Minimum age of records to be anonymized in days. Default is 0 days old.
- -x EXCLUDE, --exclude EXCLUDE: Email domain to exclude from anonymization.

### Programatic Use in Python
Here's an example:

``` python
from redacty import anonymize_records

# Connect to the PostgreSQL database
conn = psycopg2.connect(database_url)

# Anonymize email addresses in the specified table and column, set minimum age, and no excluded domains
anonymize_records(conn, table, column, 30, " ")

# Close the database connection
conn.close()
```
---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).