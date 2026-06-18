# database.py

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env if using environment variables

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'yourdbname')
DB_USER = os.getenv('DB_USER', 'youruser')
DB_PASS = os.getenv('DB_PASS', 'yourpassword')
DB_PORT = os.getenv('DB_PORT', '5432')


def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )


def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            headline TEXT,
            url TEXT,
            summary TEXT,
            source TEXT,
            scraped_at TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


def save_to_db(news_data):
    conn = connect_db()
    cursor = conn.cursor()
    for item in news_data:
        cursor.execute('''
            INSERT INTO news (headline, url, summary, source, scraped_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            item['headline'],
            item['url'],
            item['summary'],
            item['source'],
            item['scraped_at']
        ))
    conn.commit()
    cursor.close()
    conn.close()
