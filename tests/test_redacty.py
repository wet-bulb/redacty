import pytest
import psycopg2
from psycopg2 import sql
from unittest.mock import Mock
from datetime import datetime, timedelta
from redacty.redacty import anonymize_email, anonymize_records

@pytest.fixture(scope="module")
def db_conn():
    # Set up temporary test database
    db_name = "test_db"
    conn = psycopg2.connect(user="postgres", password="", host="localhost", port="5432")
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
    conn.commit()
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    conn.commit()
    cursor.close()
    conn.close()

    # Set up connection to test database
    conn = psycopg2.connect(user="postgres", password="", host="localhost", port="5432", dbname=db_name)
    cursor = conn.cursor()

    # Set up redacti table
    cursor.execute("""
        CREATE TABLE redacti (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP,
            body TEXT
        );
    """)
    yield conn
    cursor.close()
    conn.close()

    # Drop test database
    conn = psycopg2.connect(user="postgres", password="", host="localhost", port="5432")
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
    cursor.close()
    conn.close()

@pytest.fixture
def mock_input_y(monkeypatch):
    mock_input = Mock(return_value='y')
    monkeypatch.setattr('builtins.input', mock_input)
    return mock_input

@pytest.mark.parametrize("email, excluded_domain, expected_output", [
    ("test@example.com", "example.com", None),
    ("hello.world@gmail.com", "yahoo.com", "*@*"),
    ("invalid.email", "example.com", None),
])
def test_anonymize_email(email, excluded_domain, expected_output):
    assert anonymize_email(email, excluded_domain) == expected_output

def test_anonymize_records(db_conn, mock_input_y):
    cursor = db_conn.cursor()
    mock_records = [
        (1, datetime.now() - timedelta(days=35), "This is a test email to test@example.com"),
        (2, datetime.now() - timedelta(days=35), "Another test email to hello.world@gmail.com"),
        (3, datetime.now() - timedelta(days=35), "This email doesn't contain an email address"),
        (4, datetime.now(), "This email is too new to be anonymized")
    ]
    cursor.executemany("INSERT INTO redacti (id, created_at, body) VALUES (%s, %s, %s)", mock_records)
    db_conn.commit()
    cursor.close()

    anonymize_records(db_conn, "redacti", "body", 30, "example.com")
    db_conn.commit()

    cursor = db_conn.cursor()
    cursor.execute("SELECT body FROM redacti WHERE id = 1")
    assert cursor.fetchone()[0] == "This is a test email to test@example.com"

    cursor.execute("SELECT body FROM redacti WHERE id = 2")
    assert cursor.fetchone()[0] == "Another test email to *@*"

    cursor.execute("SELECT body FROM redacti WHERE id = 3")
    assert cursor.fetchone()[0] == "This email doesn't contain an email address"

    cursor.execute("SELECT body FROM redacti WHERE id = 4")
    assert cursor.fetchone()[0] == "This email is too new to be anonymized"

    cursor.close()