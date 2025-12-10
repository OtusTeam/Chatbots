import httpx
import time


def fetch_sync(url: str) -> str:
    print(f'Start  {url}')
    with httpx.Client() as client:
        response = client.get(url)
    print(f'Завершили запрос  {url}, статус {response.status_code}')
    return response.text


def run_sync_sequence() -> None:
    url_list = [
        'https://github.com',
        'https://python.org',
        'https://pypi.org',
    ]
    start_time = time.time()
    print(f'Start HTTP operation')
    for url in url_list:
        fetch_sync(url)
    print(f'End HTTP operation')
    end_time = time.time()
    total_time = end_time - start_time
    print(f'Total time: {total_time:.2f} sec')
    return total_time


def run_multi_user_simulation(user_count: int) -> None:
    print(f'=====Началась синхронная обработка {user_count} пользователей =====')
    single_user_time = run_sync_sequence()
    est_time = single_user_time * user_count

    print(f'Оценка общего времени {single_user_time:.2f} sec x {user_count} = {est_time:.2f} sec')

    start_all = time.time()

    for index in range(1, user_count + 1):
        print(f'Пользователь {index}')
        run_sync_sequence()

    end_all = time.time()
    total_all = end_all - start_all
    print(f'Оценка общего времени {single_user_time:.2f} sec x {user_count} = {est_time:.2f} sec')
    print(f'Оценка  фактического времени {total_all:.2f} sec ')

if __name__ == '__main__':
    # run_sync_sequence()
    run_multi_user_simulation(user_count=3)