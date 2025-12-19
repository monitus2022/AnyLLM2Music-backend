import time
from functools import wraps
from .logger import app_logger

def timeit(func):
    """Decorator to measure the execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        app_logger.info(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper