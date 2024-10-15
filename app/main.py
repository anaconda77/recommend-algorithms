import redis
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from scheduler import RecommendationScheduler
from eventQueue import EventQueue
from recommender import VideoRecommender

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

if __name__ == "__main__":
    redis_client = redis.Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], db=os.environ["REDIS_DATABASE"])
    recommender = VideoRecommender(redis_client)
    event_queue = EventQueue(redis_client)
    scheduler = RecommendationScheduler(recommender, event_queue)
    
    recommender.close()
    scheduler.close()