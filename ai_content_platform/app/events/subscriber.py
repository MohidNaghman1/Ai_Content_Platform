from ai_content_platform.app.shared.utils import get_redis_connection
from ai_content_platform.app.events.router import route_event
import json
import redis
import time
import uuid
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)

def create_subscriber(stream_name: str, consumer_group: str = None):
    """
    Creates a subscriber for a specific stream.
    
    :param stream_name: Redis stream to subscribe to
    :param consumer_group: Consumer group name (defaults to stream_name + '_workers')
    """
    if consumer_group is None:
        consumer_group = f"{stream_name}_workers"
    
    consumer_name = f"worker_{uuid.uuid4()}"
    redis_conn = get_redis_connection()

    # Create consumer group
    try:
        redis_conn.xgroup_create(stream_name, consumer_group, id='0', mkstream=True)
        logger.info(f"[Subscriber] Created group '{consumer_group}' on '{stream_name}'")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

    logger.info(f"[Subscriber] Listening to '{stream_name}' as '{consumer_name}'...")
    
    last_pending_check = time.time()
    PENDING_CHECK_INTERVAL = 30

    while True:
        # Handle pending messages (same as your code)
        now = time.time()
        if now - last_pending_check > PENDING_CHECK_INTERVAL:
            handle_pending_messages(redis_conn, stream_name, consumer_group, consumer_name)
            last_pending_check = now

        # Read new messages
        messages = redis_conn.xreadgroup(
            consumer_group, consumer_name, 
            {stream_name: '>'}, 
            count=10, block=5000
        )
        
        for stream, events in messages:
            for event_id, event_data in events:
                process_event(redis_conn, stream_name, consumer_group, event_id, event_data)
        
        time.sleep(0.1)


def process_event(redis_conn, stream_name, consumer_group, event_id, event_data):
    """Process a single event from the stream."""
    # Parse event
    event = {
        k.decode() if isinstance(k, bytes) else k: 
        v.decode() if isinstance(v, bytes) else v 
        for k, v in event_data.items()
    }
    
    if 'payload' in event:
        event['payload'] = json.loads(event['payload'])
    
    event['stream_id'] = event_id
    event['delivery_count'] = 1
    
    try:
        # Route to appropriate handler based on stream name
        route_event(stream_name, event)
        # Acknowledge only on success
        redis_conn.xack(stream_name, consumer_group, event_id)
    except Exception as e:
        logger.error(f"[Subscriber] Error handling event {event_id}: {e}")
        # Do NOT ack on failure


def handle_pending_messages(redis_conn, stream_name, consumer_group, consumer_name):
    """Handle pending (unacknowledged) messages."""
    try:
        pending_entries = redis_conn.xpending_range(
            stream_name, consumer_group,
            min='-', max='+', count=10
        )
        for entry in pending_entries:
            message_id, consumer, idle_time, delivery_count = entry
            if idle_time > 60000:  # 60 seconds
                try:
                    claimed = redis_conn.xclaim(
                        stream_name, consumer_group, consumer_name,
                        min_idle_time=60000, message_ids=[message_id]
                    )
                    for claimed_id, claimed_data in claimed:
                        event = {
                            k.decode() if isinstance(k, bytes) else k: 
                            v.decode() if isinstance(v, bytes) else v 
                            for k, v in claimed_data.items()
                        }
                        if 'payload' in event:
                            event['payload'] = json.loads(event['payload'])
                        event['stream_id'] = claimed_id
                        event['delivery_count'] = delivery_count
                        # Dead letter queue after 5 retries
                        if delivery_count > 5:
                            redis_conn.xadd(f'{stream_name}_dead', event)
                            redis_conn.xack(stream_name, consumer_group, claimed_id)
                            logger.info(f"[Subscriber] Moved {claimed_id} to dead-letter")
                            continue
                        try:
                            route_event(stream_name, event)
                            redis_conn.xack(stream_name, consumer_group, claimed_id)
                        except Exception as e:
                            logger.error(f"[Subscriber] Error on retry {claimed_id}: {e}")
                except Exception as e:
                    logger.error(f"[Subscriber] Error claiming {message_id}: {e}")
    except Exception as e:
        logger.error(f"[Subscriber] Error fetching pending: {e}")