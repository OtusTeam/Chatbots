from redis.asyncio import Redis

from app.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def increment_user_counter(user_id: int) -> int:
    key = f"user:{user_id}:messages"
    return int(await redis_client.incr(key))


async def get_user_counter(user_id: int) -> int:
    key = f"user:{user_id}:messages"
    value = await redis_client.get(key)
    return int(value) if value else 0


async def redis_healthcheck() -> bool:
    pong = await redis_client.ping()
    return bool(pong)
