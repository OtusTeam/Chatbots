import time
import asyncio
import httpx



URL = "https://httpbin.org/get"

async def async_get_data() -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(URL)
        response.raise_for_status()
        # if response.status_code == 200:
        data = response.json()


    print(f"HTTP status {response.status_code}")
    print(f"Data {data}")
    print(type(data))


async def main() -> None:
    # await asyncio.gather(
        await async_get_data()

    # )

start = time.perf_counter()
asyncio.run(main())

timer = time.perf_counter() - start
print(f"{timer:.5f} seconds")