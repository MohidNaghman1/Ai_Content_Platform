
# main.py or worker.py
from ai_content_platform.app.events.subscriber import create_subscriber
import threading
from ai_content_platform.app.shared.logging import get_logger
logger = get_logger(__name__)

def start_all_subscribers():
    """Start subscribers for all streams in separate threads."""
    streams = ["notifications", "user_events", "content_events"]
    threads = []
    for stream in streams:
        try:
            thread = threading.Thread(
                target=create_subscriber,
                args=(stream,),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            logger.info(f"Started subscriber for {stream}")
        except Exception as e:
            logger.error(f"Failed to start subscriber for {stream}: {e}", exc_info=True)
    # Keep main thread alive
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    start_all_subscribers()