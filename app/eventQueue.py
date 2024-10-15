import json

class EventQueue:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.queue_key = "event_queue"

    def add_event(self, event):
        self.redis.rpush(self.queue_key, json.dumps(event))

    def get_events(self, batch_size=100):
        events = []
        for _ in range(batch_size):
            event = self.redis.lpop(self.queue_key)
            if event is None:
                break
            events.append(json.loads(event))
        return events
