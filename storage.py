import logging
from database import get_connection, release_connection

# Saves valid snapshots to database
def add_valid_snapshot(time, value, tags):

    # Gets connection from pool and create cursor
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO valid_snapshots (time, value, tags)
            VALUES (%s, %s, %s)
        """, (time, value, tags))

        # Save changes 
        connection.commit()

    except Exception as e:
        logging.error(f"Error inserting valid snapshot into database: {e}")
        raise

    finally:
        # Close cursor release connection from pool
        cursor.close()
        release_connection(connection)
