import asyncio

from app.cache.redis import redis_healthcheck
from app.storage.postgres import postgres_healthcheck


async def run_smoke() -> int:
    pg_ok = await postgres_healthcheck()
    redis_ok = await redis_healthcheck()
    print({"postgres": pg_ok, "redis": redis_ok})
    return 0 if pg_ok and redis_ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_smoke()))
