from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from fastapi.logger import logger
import logging

class RecommendationScheduler:
    def __init__(self, recommender, event_queue):
        self.recommender = recommender
        self.event_queue = event_queue
        self.scheduler = BackgroundScheduler()
        self.setup_scheduler()

    def setup_scheduler(self):
        # 유저 추천 알고리즘
        self.scheduler.add_job(
            func=self.process_user_algorithms_events,
            trigger=IntervalTrigger(seconds=5),  # 5분마다 실행
            id='user_recommendation_update',
            name='Update all user recommendations daily',
            replace_existing=True
        )
        
        # 기본 추천 알고리즘
        self.scheduler.add_job(
            func=self.process_default_algorithms_events,
            trigger=IntervalTrigger(seconds=10),  # 12시간마다 실행
            id='default_recommendation_update',
            name='Update all default recommendations daily',
            replace_existing=True
            )
        
        self.scheduler.start()

    def process_default_algorithms_events(self):
        category_ids = [i for i in range(1,6)]

        for category_id in category_ids:
            self.recommender.run_default_algorithm(category_id)
        logger.debug("runned default algorithm")
        
    def process_user_algorithms_events(self):
        events = self.recommender.event_queue.get_events()
        for event in events:
            event_time = event['last_updated_at']
            if event_time is None:
                  self.recommender.run_algorithm(
                    event['member_id'], 
                    event['category_id']
                )
            else:
                logger.debug(event_time)
                time_difference = datetime.now() - datetime.fromisoformat(event_time)
                
                if time_difference >= timedelta(seconds=10):
                    self.recommender.run_algorithm(
                        event['member_id'], 
                        event['category_id']
                    )
                    logger.debug(f"runned alogorithm, member_id:{event['member_id']}")
                else:
                    self.recommender.event_queue.add_event(event)
        
    def close(self):
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown successfully")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")

