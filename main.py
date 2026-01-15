from satellite import get_snapshots
from api import start_api
import time
import threading

# Run Flask server in background thread
api_thread = threading.Thread(target=start_api, daemon=True)
api_thread.start()

# Fetch and validate snapshots once per second
while True:
    get_snapshots()
    time.sleep(1)