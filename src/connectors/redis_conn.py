from redis.asyncio import Redis

from src.config import settings


# new_case: создает экземпляр redis_client с кастомными методами
class RedisManager:
    def __init__(self, host: str, port: int):
        self.redis_client: Redis | None = None
        self.host = host
        self.port = port

    async def connect(self):
        self.redis_client = Redis(host=self.host, port=self.port, decode_responses=True)
        print("Redis подключен")

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        if self.redis_client is None:
            raise RuntimeError("Redis is not connected.")
        return await self.redis_client.set(name=key, value=value, ex=ex)

    async def get(self, key: str) -> str | None:
        if self.redis_client is None:
            raise RuntimeError("Redis is not connected.")
        return await self.redis_client.get(name=key)

    async def delete(self, key: str) -> int:
        if self.redis_client is None:
            raise RuntimeError("Redis is not connected.")
        return await self.redis_client.delete(key)

    async def keys(self, pattern: str = "*") -> list[str]:
        if self.redis_client is None:
            raise RuntimeError("Redis is not connected.")
        return await self.redis_client.keys(pattern)

    async def close(self, pattern: str = "*"):
        if self.redis_client:
            await self.redis_client.aclose()
            print("Redis отключен")


redis = RedisManager(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
