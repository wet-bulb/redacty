import argparse
from datetime import datetime, timedelta
import psycopg2
import re


def anonymize_email(email, excluded_domain):
    """Anonymizes email address by replacing characters before '@' with '*'.

    Args:
    email (str): Email address to be anonymized.
    excluded_domain (str): Email domain to exclude from anonymization.

    Returns:
    str: Anonymized email address.
    """
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(email_regex, email) and not email.endswith(excluded_domain):
        return re.sub(r'[a-zA-Z0-9._%+-]+', '*', email)
    else:
        return None


def anonymize_records(conn, table, column, days, excluded_domain):
    """Anonymizes email addresses in database records that are older than the specified number of days.

    Args:
    conn (psycopg2.extensions.connection): Postgres database connection.
    table (string): Name of the table that holds the column to redact.
    column (string): Name of the column that holds the text to redact.
    days (int): Number of days used to filter records by age.
    excluded_domain (str): Email domain to exclude from anonymization.

    Returns:
    None
    """
    try:
        if days <= 0:
            raise ValueError("Number of days must be greater than zero.")
        cursor = conn.cursor()
        today = datetime.now().date()
        threshold = today - timedelta(days=days)
        query = "SELECT id, created_at, {column} FROM {table} WHERE DATE(created_at) <= %s AND {column} IS NOT NULL AND {column} ~* '.*[a-z0-9._+-]+@(?!{excluded_domain})[a-z0-9.-]+.[a-z]{{2,}}.*'".format(excluded_domain=excluded_domain, column=column, table=table)


        cursor.execute(query, (threshold,))
        records = cursor.fetchall()

        total_records = 0
        for record in records:
            total_records += 1
            record_id = record[0]
            body = record[2]

            # Anonymize email addresses
        
            email_regex = r'\b[A-Za-z0-9._%+-]+@(?!{})[A-Za-z0-9.-]+\.[A-Z|a-z]{{2,}}\b'.format(excluded_domain)
            matches = re.findall(email_regex, body)
            for match in matches:
                anonymized_email = anonymize_email(match, excluded_domain)
                if anonymized_email:
                    body = body.replace(match, anonymized_email)

            # Update database record
            if body != record[2]:
                query = f"UPDATE {table} SET {column} = '{body}' WHERE id = {record_id}"
                cursor.execute(query)

        if total_records > 0:
            confirm = input(f"{total_records} records will be anonymized. Proceed? (y/N) ")
            if confirm.lower() == 'y':
                conn.commit()
                print(f"{total_records} records anonymized.")
            else:
                conn.rollback()
                print("Anonymization cancelled.")
        else:
            print("No records to anonymize.")

        cursor.close()
    except ValueError as ve:
        print(f"ValueError: {str(ve)}")
        return None

    except psycopg2.Error as e:
        print(f"Database error: {str(e)}")
        return None



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Anonymize email addresses in a PostgreSQL database.")
    excluded_domain = " "
    days = 0

    parser.add_argument("url", metavar="DATABASE_URL", help="PostgreSQL database URL")
    parser.add_argument("-a", "--age", default=0, type=int, help="Minimum age of records to be anonymized in days. Default is 0 days old.")
    parser.add_argument("-x", "--exclude", default=" ", help="Email domain to exclude from anonymization.")


    args = parser.parse_args()

    target_db = args.url
    days = args.age
    excluded_domain = args.exclude

    conn = psycopg2.connect(target_db)

    # Anonymize records
    anonymize_records(conn, days, excluded_domain)

    # Close database connection
    conn.close()