import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool
import logging

# Retrieve environment variables from .env file
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

connection_pool = None

# Connects to database and creates tables when application is started
def init_db():

    logging.info("Connecting to database...")
    global connection_pool

    try:
        # Create connection pool
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        logging.info("Connection pool created successfully")

        # Requests connection from the pool
        connection = connection_pool.getconn()
        cursor = connection.cursor()

        # Create table for valid_snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS valid_snapshots(
                id SERIAL PRIMARY KEY,
                time TIMESTAMP NOT NULL,
                value REAL NOT NULL,
                tags TEXT[] NOT NULL
            )
        """)

        connection.commit()
        logging.info("valid_snapshots table created successfully")

        # Close cursor and return connection
        cursor.close()
        connection_pool.putconn(connection)

    except Exception as e:
        logging.error(f"Error connecting to database: {e}")