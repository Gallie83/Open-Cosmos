from satellite import get_snapshots
from api import start_api
from database import init_db, close_pool
import time
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('snapshots.log'),
        logging.StreamHandler()
    ]
)
def main():
    try:
        init_db()

        # Run Flask server in background thread
        api_thread = threading.Thread(target=start_api, daemon=True)
        api_thread.start()

        # Fetch and validate snapshots once per second
        while True:
            get_snapshots()
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Shutting down servers...")
        close_pool()

    except Exception as e:
        logging.error(f"Application error: {e}")
        close_pool()
        raise

if __name__ == '__main__':
    main()