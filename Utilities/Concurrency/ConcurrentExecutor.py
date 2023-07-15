import concurrent.futures

class ConcurrentExecutor:
    def __init__(self):
        pass

    def execute_concurrently(self, items: list, target_func):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Execute the target function concurrently using ThreadPoolExecutor
            executor.map(target_func, items)