import asyncio


async def simulate_io_step(name: str, delay: float) -> None:
    print(f'Start operation: {name}, delay {delay} sec')
    await asyncio.sleep(delay)
    await asyncio.sleep(delay)
    print(f'End operation: {name}')


async def async_scenario() -> None:
    print(f'Start Async operation')
    await simulate_io_step(name='Подготовка данных 1', delay=3)
    await simulate_io_step(name='Подготовка данных 2', delay=2)
    await simulate_io_step(name='Подготовка данных 3', delay=3)
    print(f'End Async operation')


# async def async_scenario() -> None:
#     print(f'Start Async operation')
#     responses = await asyncio.gather(
#         simulate_io_step(name='Подготовка данных 1', delay=4),
#         simulate_io_step(name='Подготовка данных 2', delay=3),
#         simulate_io_step(name='Подготовка данных 3', delay=2),
#         simulate_io_step(name='Подготовка данных 1', delay=4),
#     )
#     print(f'End Async operation')


if __name__ == '__main__':
    asyncio.run(async_scenario())
