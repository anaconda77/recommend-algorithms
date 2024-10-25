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
        for i in range(1,6):
            for j in range(1,11):
                recommender.add_videoInfo(i, j, datetime.now())
                logger.debug(f"Added video info: category {i}, id {j}")
    
    def make_events(self, recommender):
        for i in range(1,11):
            for j in range(100):
                if i % 2 == 0:
                    recommender.get_new_event(1,1,i,True,False)
                else:
                    recommender.get_new_event(1,1,i,True,True)
    
    
    def close(self):
        self.redis.close()