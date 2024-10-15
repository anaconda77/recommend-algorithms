import redis
import json
from datetime import datetime
from eventQueue import EventQueue

class VideoRecommender:
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.event_queue = EventQueue(self.redis)
    
    def add_videoInfo(self, video_id, created_at):
        video_key = f"video:{video_id}"
        self.redis.hset(video_key, mapping={
            "created_at" : created_at.isoformat(),
            "view_count" : 0,
            "like_count" : 0
        })
    
    # 유저의 행위로 이벤트 발생, 스케줄러에 추천 영상 리스트 계산 작업 요청 추가
    def get_new_event(self, user_id, video_id, watched=False, liked=False):
        reaction_key = f"reaction:{user_id}:{video_id}"
        video_key = f"video:{video_id}"
        
        if watched:
            self.redis.hset(reaction_key, "watched", 1)
            self.redis.hincrby(video_key, "view_count", 1)
        if liked == 1:
            self.redis.hset(reaction_key, "liked", 1)
            self.redis.hincrby(video_key, "like_count", 1)
        elif liked == -1:
            self.redis.hset(reaction_key, "liked", 0)
            # self.redis.hset(video_key, "like_count", -1)
        
        new_event = {
            "user_id" : user_id,
            "last_updated_at" : self.redis.hget(f"user_meta:{user_id}", "last_updated_at")
        }
        
        self.event_queue.add_event(new_event)
    
    # 실제 계산이 수행되는 알고리즘
    def run_algorithm(self, user_id, video_id):
        return True

    def update_scores(self, user_id, video_id):
        score = self.run_algorithm(user_id, video_id)
        score_key = f"scores:{user_id}"
        self.redis.zadd(score_key, {video_id: score})
        self.redis.hset(f"user_meta:{user_id}", "last_updated_at", datetime.now().isoformat())
        
    # 계산된 추천 데이터를 받아온다.
    def get_recommendations(self, user_id, count=10):
        score_key = f"scores:{user_id}"
        recommendation_list = self.redis.zrevrange(score_key, 0, count - 1) # 내림차순 정렬 반환
        last_updated_at = self.redis.hget(f"user_meta:{user_id}", "last_updated_at")
        
        result = {
            "user_id" : user_id, 
            "recommend_videos" : [
                rec.decode() for rec in recommendation_list
            ],
            "last_updated_at" : last_updated_at
        }
        
        return json.dumps(result)
    
    def close(self):
        self.redis.close()