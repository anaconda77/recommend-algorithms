from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta

class RecommendationScheduler:
    def __init__(self, recommender, event_queue):
        self.recommender = recommender
        self.event_queue = event_queue
        self.scheduler = BackgroundScheduler()
        self.setup_scheduler()

    def setup_scheduler(self):
        self.scheduler.add_job(
            func=self.process_events,
            trigger=IntervalTrigger(hours=24),  # 매일 실행
            id='daily_recommendation_update',
            name='Update all user recommendations daily',
            replace_existing=True)
        self.scheduler.start()

    def process_events(self):
        events = self.recommender.event_queue.get_events()
        for event in events:
            event_time = datetime.fromisoformat(event['last_updated_at'])
            time_difference = datetime.now() - event_time
            
            if time_difference >= timedelta(minutes=10):
                self.recommender.run_algorithm(
                    event['user_id'], 
                    event['video_id']
                )
            else:
                self.recommender.event_queue.add_event(event)
        
    def close(self):
        self.scheduler.shutdown()
