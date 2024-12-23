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
import uvicorn
from app.demoCreator import DemoCreator

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 전역 변수로 선언
redis_client = None
recommender = None
event_queue = None
scheduler = None

@app.on_event("startup")
async def startup_event():
    global redis_client, recommender, event_queue, scheduler
    
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DATABASE", 0)),
            socket_connect_timeout=5,  # 연결 타임아웃 설정
            retry_on_timeout=True 
        )
        recommender = VideoRecommender(redis_client)
        event_queue = EventQueue(redis_client)
        scheduler = RecommendationScheduler(recommender, event_queue)
        logger.info("Application started successfully")
        
        # demoCreator = DemoCreator(redis_client)
        # demoCreator.make_demo_videos(recommender)
        # demoCreator.make_events(recommender)
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
    if recommender:
        recommender.close()
    if scheduler:
        scheduler.close()
    if redis_client:
        redis_client.close()
    logger.info("Application shut down complete")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)