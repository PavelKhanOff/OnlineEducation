from typing import Optional
from app.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from aioredis import Redis
import redis
import aioredis.sentinel


class RedisCache:
    def __init__(self, password=None):
        self.redis_cache: Optional[Redis] = None
        self._password = password

    async def init_cache(self):

        sentinel = aioredis.sentinel.Sentinel(
            [
                ("sentinel-0.sentinel.default.svc.cluster.local", 5000),
                ("sentinel-2.sentinel.default.svc.cluster.local", 5000),
                ("sentinel-1.sentinel.default.svc.cluster.local", 5000),
            ]
        )
        self.redis_cache = sentinel.master_for('mymaster')

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value):
        return await self.redis_cache.set(key, value)

    async def hset(self, name, mapping):
        return await self.redis_cache.hset(name, mapping=mapping)

    async def hget(self, name, key):
        return await self.redis_cache.hget(name, key)

    async def get(self, key):
        return await self.redis_cache.get(key)

    async def close(self):
        self.redis_cache.close()
        await self.redis_cache.wait_closed()


redis_cache = RedisCache(password=REDIS_PASSWORD)


class RedisPublisher:
    def __init__(self, host='redis', port=6380, password=None, username="default"):
        self._host = host
        self._port = port
        self._password = password
        self._username = username
        self._conn = self.init_redis_connection()

    def init_redis_connection(self):
        """Initialize redis_conf connection"""
        return redis.Redis(
            host=self._host,
            port=self._port,
            password=self._password,
            username=self._username,
        )

    def keys(self, pattern):
        return self._conn.keys(pattern)

    def set(self, key, value):
        return self._conn.set(key, value)

    def hset(self, name, mapping):
        return self._conn.hset(name, mapping=mapping)

    def hget(self, name, key):
        return self._conn.hget(name, key)

    def get(self, key):
        return self._conn.get(key)

    def __del__(self):
        """Disconnect"""
        return self._conn.connection_pool.disconnect()


redis_pub = RedisPublisher(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
