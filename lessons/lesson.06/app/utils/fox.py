import asyncio
import httpx


async def async_fox() -> str:
    URL = "https://randomfox.ca/floof/"
    async with httpx.AsyncClient() as client:
        response = await client.get(URL)
        response.raise_for_status()
        data = response.json().get("image")
        return data


async def main() -> None:
        result = await async_fox()


if __name__ == '__main__':
    asyncio.run(main())
