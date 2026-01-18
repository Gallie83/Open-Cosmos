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

def get_valid_snapshots(start, end):
    
    # Gets connection from pool and create cursor
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Query valid_snapshots table
        cursor.execute("""
            SELECT time, value, tags 
            FROM valid_snapshots
            WHERE time >= %s AND time <= %s
        """, (start, end))

        # rows is returned as list of tuples
        rows = cursor.fetchall()

        snapshots = []
        # Map rows into list of dictionaries
        for row in rows:
            snapshots.append({
                'time': row[0].isoformat(),
                'value': row[1],
                'tags': row[2]
            })

        return snapshots

    except Exception as e:
        logging.error(f"Error reading valid snapshot in database: {e}")
        raise

    finally:
        # Close cursor release connection from pool
        cursor.close()
        release_connection(connection)

# Saves discarded snapshots to database
def add_discarded_snapshot(time, value, tags, reason, discarded_at):

    # Gets connection from pool and create cursor
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO discarded_snapshots (time, value, tags, reason, discarded_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (time, value, tags, reason, discarded_at))

        # Save changes 
        connection.commit()

    except Exception as e:
        logging.error(f"Error inserting discarded snapshot into database: {e}")
        raise

    finally:
        # Close cursor release connection from pool
        cursor.close()
        release_connection(connection)

def get_discarded_snapshots(start, end, reason):
    
    # Gets connection from pool and create cursor
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Query discarded_snapshots table
        cursor.execute("""
            SELECT time, value, tags, reason, discarded_at
            FROM discarded_snapshots
            WHERE time >= %s AND time <= %s
        """, (start, end))

        # rows is returned as list of tuples
        rows = cursor.fetchall()

        # Filter by reason if provided
        if reason:
            filtered_rows = [row for row in rows if row[3] == reason]
        else: 
            filtered_rows = rows
        snapshots = []

        # Map rows into list of dictionaries
        for row in filtered_rows:
            snapshots.append({
                'time': row[0].isoformat(),
                'value': row[1],
                'tags': row[2],
                'reason': row[3],
                'discarded_at': row[4]
            })

        return snapshots

    except Exception as e:
        logging.error(f"Error reading discarded snapshot in database: {e}")
        raise

    finally:
        # Close cursor release connection from pool
        cursor.close()
        release_connection(connection)
