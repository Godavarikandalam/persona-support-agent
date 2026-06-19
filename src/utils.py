"""
utils.py
--------
Shared retry helper so transient Gemini API overload (503 errors) doesn't
crash the whole app - it just waits and tries again a few times.
"""

import time
import random


def call_with_backoff(func, *args, max_retries=4, **kwargs):
    """Call func(*args, **kwargs), retrying with exponential backoff if it
    raises an exception (e.g. a 503 'model overloaded' error)."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if attempt == max_retries - 1:
                raise
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)
    raise last_error