#!/usr/bin/env python3
import sys
import base64
import psycopg2
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
SCOPE = "ticketing"
KEY = "lakebase-url"

def get_connection_url():
    try:
        secret = w.secrets.get_secret(scope=SCOPE, key=KEY)
        return base64.b64decode(secret.value).decode("utf-8")
    except Exception as e:
        print(f"\nError: Could not retrieve connection URL from secrets")
        print(f"Run setup_secrets.py first to configure the connection.\n")
        sys.exit(1)

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'open',
                priority VARCHAR(20) DEFAULT 'medium',
                category VARCHAR(100),
                created_by VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ticket_messages (
                message_id SERIAL PRIMARY KEY,
                ticket_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                author VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id)")
        conn.commit()
        print("Tables created successfully")

if __name__ == "__main__":
    connection_url = get_connection_url()
    conn = psycopg2.connect(connection_url)
    create_tables(conn)
    conn.close()
    print("Database initialization complete!")