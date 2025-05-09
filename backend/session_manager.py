# backend/session_manager.py

import redis
import os
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def add_message(session_id, role, text):
    msg = {"role": role, "text": text}
    r.rpush(session_id, json.dumps(msg))
    r.expire(session_id, 1800)  # 30 mins TTL

def get_history(session_id):
    messages = r.lrange(session_id, 0, -1)
    return [json.loads(m) for m in messages]

def clear_session(session_id):
    r.delete(session_id)
