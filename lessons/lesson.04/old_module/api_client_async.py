import httpx
import time
import asyncio


async def fetch_async(url: str) -> str:
    print(f'Start  {url}')
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)

        response.raise_for_status()
        print(f'Завершили запрос  {url}, статус {response.status_code}')
        body_text = response.text
        print(f'Длина тела ответа {len(body_text)} символов')
        return body_text
    except httpx.HTTPError as error:
        print(f'Произошла ошибка {error}')
        return ''


async def fetch_many_async():
    services = {
        'time': "https://timeapi.io/api/Time/current/zone?timeZone=Europe/Moscow",
        'quota': "https://dummyjson.com/quotes/random",
        'crypta': "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
    }
    print(f'=====Запустили  асинхронные запросы =====')
    # tasks = [fetch_async(url=url) for url in services.values()]
    tasks = [fetch_async(url=url1), fetch_async(url=url2), fetch_async(url=url3)]
    print(f'=====Готово {len(tasks)} корутин для запуска =====')
    start = asyncio.get_event_loop().time()
    responses = await asyncio.gather(*tasks)
    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start
    print(f'=====Все запросы выполнелись за  {total_time:.2f} ')
    result = {}
    for service_name, response_body in zip(services.keys(), responses):
        result[service_name] = response_body
        print(f'Сервис {service_name}')
        print(f'Первые символы ответа {response_body[:70]}')
    return result


async def async_main() -> None:
    print(f'=====Началась асинхронная обработка HTTP =====')
    summary = await fetch_many_async()

    print(f'=====Завершилась асинхронная обработка HTTP =====')
    if not summary:
        print('Пустой ответ')


if __name__ == '__main__':
    asyncio.run(async_main())


[a, b, c, d]