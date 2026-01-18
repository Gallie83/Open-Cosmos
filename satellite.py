import requests
import time
from datetime import datetime
from storage import snapshot_storage, discarded_snapshots
import logging

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

        # Validate snapshot age
        if snapshot_age > 3600:
            logging.warning(f'Snapshot over 1hr old, disregard: {snapshot}')
            discarded_snapshots.append({ 
                'time': snapshot_time, 
                'value': snapshot['value'], 
                'tags': snapshot['tags'], 
                'reason': 'age' 
                })
            return

        # Validate snapshot tags
        elif 'system' in snapshot['tags']:
            logging.warning(f'Invalid system tag: {snapshot}')
            discarded_snapshots.append({ 
                'time': snapshot_time, 
                'value': snapshot['value'], 
                'tags': snapshot['tags'], 
                'reason': 'system' 
                })
            return
        elif 'suspect' in snapshot['tags']: 
            logging.warning(f'Invalid suspect tag: {snapshot}')
            discarded_snapshots.append({ 
                'time': snapshot_time, 
                'value': snapshot['value'], 
                'tags': snapshot['tags'], 
                'reason': 'suspect' 
                })
            return

        # Print valid snapshots and append to snapshots list in storage.py
        tag = snapshot['tags'][0]
        temp = snapshot['value']
        time_str = datetime.fromtimestamp(snapshot['time'])
                                          
        logging.info(f"Valid {tag} snapshot measuring {temp}°C at {time_str.strftime('%H:%M:%S')}")
        snapshot_storage.append({ 
            'time': snapshot_time, 
            'value': snapshot['value'], 
            'tags': snapshot['tags'] 
            })

    except Exception as e:
        logging.error(f"Fetch error: {e}")