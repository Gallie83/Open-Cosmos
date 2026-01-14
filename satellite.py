import requests
import time
from datetime import datetime

def get_snapshots():
    try:
        # Fetch snapshot data
        response = requests.get('http://localhost:28462/')

        # Early return if bad status code
        if response.status_code == 404:
            print("No data currently available")
            return
        
        if response.status_code != 200:
            print(f"Unexpected status code: {response.status_code}")
            return

        snapshot = response.json()

        current_time = time.time()
        snapshot_age = current_time - snapshot['time']


        # Validate snapshot age
        if snapshot_age > 3600:
            # print("Snapshot over 1hr old, disregard")
            return

        # Validate snapshot tags
        if 'system' in snapshot['tags']:
            # print('Invalid snapshot tag: System')
            return
        elif 'suspect' in snapshot['tags']: 
            # print('Invalid snapshot tag: Suspect')
            return

        # Print valid snapshots
        print(f"Valid '{snapshot['tags'][0]}' snapshot measuring {snapshot['value']}°C at {datetime.fromtimestamp(snapshot['time']).strftime('%H:%M:%S')}")

    except Exception as e:
        print(f"Fetch error: {e}")