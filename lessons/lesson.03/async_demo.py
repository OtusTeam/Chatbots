import time
import asyncio


async def async_operation(name: str, delay: int) -> None:
    print(f"{name} start operation...")
    await asyncio.sleep(delay)
    print(f"{name} stop operation...")


async def main() -> None:
    await asyncio.gather(
        async_operation("Sync1", 5),
        async_operation("Sync2", 3),
        async_operation("Sync3", 4),
        async_operation("Sync4", 2),
        async_operation("Sync5", 1)
    )

start = time.perf_counter()
asyncio.run(main())

timer = time.perf_counter() - start
print(f"{timer:.5f} seconds")