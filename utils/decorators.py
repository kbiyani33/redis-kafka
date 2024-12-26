import time
import logging
from functools import wraps
from fastapi import Request

# Configure logger
logger = logging.getLogger("time_logger")
logger.setLevel(logging.INFO)

# Decorator to log time taken by the API
def log_api_endpoint_execution_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # check for request keyword argument here to get the API endpoint
        request = kwargs.get("request")
        if not request:
            for arg in args:
                if not isinstance(arg, Request):
                    continue
                request = arg
                break
        if not request:
            logger.error("this method is not an API endpoint. Cannot use this decorator")
            raise ValueError("this method is not an API endpoint. Cannot use this decorator")

        start_time = time.perf_counter()  # Start time
        response = await func(*args, **kwargs)  # Call the original function
        end_time = time.perf_counter()  # End time
        duration = end_time - start_time
        logger.info(f"API endpoint {request.url.path} and function name {func.__name__} took {duration:.2f} seconds.")
        return response

    return wrapper
