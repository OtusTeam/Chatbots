import asyncio
import os

import httpx


async def check_health() -> dict:
    url = os.getenv("HEALTHCHECK_URL", "http://localhost:8000/health")
    async with httpx.AsyncClient(timeout=4.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    result = asyncio.run(check_health())
    print(result)
