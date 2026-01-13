import time
from satellite import get_snapshots

# Fetch and validate snapshots once per second
while True:
    get_snapshots()
    time.sleep(1)