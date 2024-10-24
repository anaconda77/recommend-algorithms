import redis
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.scheduler import RecommendationScheduler
from app.eventQueue import EventQueue
from app.recommender import VideoRecommender
from datetime import datetime
from fastapi.logger import logger
import logging

class DemoCreator:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.event_queue = EventQueue(self.redis)
    
    def make_demo_videos(self, recommender):
        for i in range(10):
            recommender.add_videoInfo(1, i, datetime.now())
            logger.debug(f"Added video info: category 1, id {i}")
    
    def make_events(self, recommender):
        for i in range(10):
            for j in range(100):
                if i % 2 == 0:
                    recommender.get_new_event(1,1,i,True,False)
                else:
                    recommender.get_new_event(1,1,i,True,True)
    
    
    def close(self):
        self.redis.close()