import argparse

import psycopg2

from redacty.redacty import anonymize_records

parser = argparse.ArgumentParser(description="Anonymize email addresses in a PostgreSQL database.")

parser.add_argument("url", metavar="DATABASE_URL", help="PostgreSQL database URL")
parser.add_argument("table", metavar="TABLE", help="PostgreSQL database table")
parser.add_argument("column", metavar="COLUMN", help="PostgreSQL database column")

parser.add_argument(
    "-a",
    "--age",
    default=0,
    type=int,
    help="Minimum age of records to be anonymized in days. Default is 0 days old.",
)
parser.add_argument("-x", "--exclude", default=" ", help="Email domain to exclude from anonymization.")

args = parser.parse_args()

target_db = args.url
table = args.table
column = args.column
days = args.age
excluded_domain = args.exclude

conn = psycopg2.connect(target_db)

# Anonymize records
anonymize_records(conn, table, column, days, excluded_domain)

# Close database connection
conn.close()
