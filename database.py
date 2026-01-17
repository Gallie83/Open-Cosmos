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

        try:
            # Create table for valid_snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS valid_snapshots(
                    id SERIAL PRIMARY KEY,
                    time TIMESTAMP NOT NULL,
                    value REAL NOT NULL,
                    tags TEXT[] NOT NULL
                )
            """)

            # Add indexing for time queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_valid_time
                ON valid_snapshots(time)
            """)

            # Create table for discarded_snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discarded_snapshots(
                    id SERIAL PRIMARY KEY,
                    time TIMESTAMP NOT NULL,
                    value REAL NOT NULL,
                    tags TEXT[] NOT NULL,
                    reason TEXT NOT NULL
                )
            """)

            # Add indexing for time queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_discarded_time
                ON discarded_snapshots(time)
            """)

            connection.commit()
            logging.info("Database tables created successfully")

        finally:    
            # Ensure cursor closes and connection is returned
            cursor.close()
            connection_pool.putconn(connection)

    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise