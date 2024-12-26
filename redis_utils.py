import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Redis Client
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_from_cache(key):
    return redis_client.get(key)

def set_to_cache(key, value, ttl=3600):
    redis_client.set(key, value, ex=ttl)

def invalidate_cache(key):
    redis_client.delete(key)
