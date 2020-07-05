from functools import wraps
import logging
from time import time


def time_printer(func):
    @wraps(func)
    def magic(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        logging.info(f"=================> Running time {func.__name__}: {end - start}")
        return result

    return magic
