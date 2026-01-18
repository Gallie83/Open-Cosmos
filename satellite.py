import requests
import time
from datetime import datetime
import logging
from storage import add_valid_snapshot, add_discarded_snapshot


def get_snapshots():
    try:
        # Fetch snapshot data
        response = requests.get('http://localhost:28462/')

        # Early return if bad status code
        if response.status_code == 404:
            logging.info("No data currently available from satellite: 404")
            return
        
        if response.status_code != 200:
            logging.error(f"Unexpected status code: {response.status_code}")
            return

        snapshot = response.json()

        # Calculate snapshots age
        current_time = time.time()
        snapshot_age = current_time - snapshot['time']

        # Convert timestamp to datetime object
        snapshot_time = datetime.fromtimestamp(snapshot['time'])

        time_now = datetime.now()

        # Validate snapshot age, save to discarded_snapshots if fails
        if snapshot_age > 3600:
            logging.warning(f'Snapshot over 1hr old, disregard: {snapshot}')
            add_discarded_snapshot( 
                snapshot_time, 
                snapshot['value'], 
                snapshot['tags'], 
                'age',
                time_now
                )
            return

        # Validate snapshot tags, save to discarded_snapshots if fails
        elif 'system' in snapshot['tags']:
            logging.warning(f'Invalid system tag: {snapshot}')
            add_discarded_snapshot( 
                snapshot_time, 
                snapshot['value'], 
                snapshot['tags'], 
                'system',
                time_now
                )
            return
        elif 'suspect' in snapshot['tags']: 
            logging.warning(f'Invalid suspect tag: {snapshot}')
            add_discarded_snapshot( 
                snapshot_time, 
                snapshot['value'], 
                snapshot['tags'], 
                'suspect',
                time_now
                )
            return

        # Log valid snapshots and save to database
        tag = snapshot['tags'][0]
        temp = snapshot['value']
        time_str = datetime.fromtimestamp(snapshot['time'])
                                          
        logging.info(f"Valid {tag} snapshot measuring {temp}°C at {time_str.strftime('%H:%M:%S')}")
        add_valid_snapshot(snapshot_time, snapshot['value'], snapshot['tags'])

    except Exception as e:
        logging.error(f"Fetch error: {e}")