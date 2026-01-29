import time


def simulator_long_operation(name: str, delay: float) -> None:
    print(f'Start operation: {name}, delay {delay} sec')
    time.sleep(delay)
    print(f'End operation: {name}')


def run_sync_operation() -> None:
    start_time = time.time()
    print(f'Start sync operation')
    simulator_long_operation('sync_operation 1', 2.0)
    simulator_long_operation('sync_operation 2', 3.0)
    simulator_long_operation('sync_operation 3', 4.0)
    end_time = time.time()
    total_time = end_time - start_time
    print(f'End sync operation')
    print(f'Total time: {total_time:.2f} sec')


if __name__ == '__main__':
    run_sync_operation()