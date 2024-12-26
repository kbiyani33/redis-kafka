import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_from_cache(key):
    return redis_client.get(key)

def set_to_cache(key, value, ttl=300):
    redis_client.set(key, json.dumps(value), ex=ttl)

def invalidate_cache(key):
    redis_client.delete(key)
