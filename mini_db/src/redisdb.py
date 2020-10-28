import pickle

from redis.client import Redis
from redlock.lock import RedLockFactory

class RedisDB(object):
    def __init__(self, redis_url):
        self._client = Redis.from_url(redis_url, decode_responses=True)

    @property
    def client(self):
        """get Redis detail obj"""
        return self._client



def redis_init():
    """
    init Redis manager obj, Redis public lock 全局锁
    """
    global redis_db, redis_lock
    redis_db = RedisDB('redis://127.0.0.1:6379/11')
    redis_lock = RedLockFactory([redis_db.client]).create_lock
    return redis_db, redis_lock

# FIXME
redis_db = redis_init()[0]
redis_lock = redis_init()[1]