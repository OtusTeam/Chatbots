import time


# print("Block Demo 1")
# time.sleep(2)
# print("Block Demo 2")
# time.sleep(2)
# print("Block Demo 3")
# time.sleep(2)

def sync_operation(name: str, delay: int) -> None:
    print(f"{name} start operation...")
    time.sleep(delay)
    print(f"{name} stop operation...")


start = time.perf_counter()
sync_operation("Sync1", 2)
sync_operation("Sync2", 3)
sync_operation("Sync3", 4)
sync_operation("Sync4", 5)
sync_operation("Sync5", 1)


timer = time.perf_counter() - start
print(f"{timer:.5f} seconds")