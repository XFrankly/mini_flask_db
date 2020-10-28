import functools
import hashlib
import inspect
import logging

from src.redisdb import redis_db

# 缓存过期时间 & 7 * 24 小时
CACHE_EXPIRE = 7 * 86400

def cache(key=None, condition=None, expire=CACHE_EXPIRE, dumps=True, callback=None):
    pass

def put(key=None, condition=None, expire=CACHE_EXPIRE, dumps=True):
    pass

def evict(key=None, condition=None):
    pass

def _eval(func, key, condition, *args, **kwargs):
    pass

def _key_gen(func, condition, *args, **kwargs):
    pass



class CacheObj(object):
    """缓存工具对象"""
    def __init__(self, cache_prefix, expire=CACHE_EXPIRE, dumps=True):
        self.dumps = dumps
        self.expire = expire
        self.cache_prefix = cache_prefix

    def set(self, key, value):
        """更新数据到缓存"""
        return redis_db.set(f"{self.cache_prefix}:{key}", value, self.expire, self.dumps)

    def get(self, key):
        """从缓存获取数据"""
        return redis_db.get(f"{self.cache_prefix}:{key}", self.dumps)

    def clear(self, key):
        """清空缓存数据"""
        return redis_db.client.delete(f"{self.cache_prefix}", self.dumps)

