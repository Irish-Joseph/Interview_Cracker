"""
Topic: Retry decorator with exponential backoff and jitter.

Concepts:
- Decorators with *args/**kwargs passthrough
- functools.wraps to preserve the wrapped function's metadata
- Exponential backoff with full jitter
- Distinguishing retryable vs fatal exceptions
- Deterministic testing by injecting the sleep function

A "retry with backoff" wrapper makes a flaky operation (network call,
database lock, API rate limit) eventually succeed without blocking
forever on a hard failure.

Backoff schedule here (base=0.1s, cap=5s, full jitter):
    attempt 1 fails -> sleep uniform(0, 0.1)
    attempt 2 fails -> sleep uniform(0, 0.2)
    attempt 3 fails -> sleep uniform(0, 0.4)
    ...
Time Complexity: worst case O(max_attempts * (call + cap))
"""

import functools
import random
import time
from typing import Callable


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 5.0,
    retryable: tuple = (Exception,),
    sleep: Callable[[float], None] = time.sleep,
):
    """Return a decorator that retries a flaky function.

    Args:
        max_attempts: total number of tries (1 = no retry).
        base_delay:   initial backoff window in seconds.
        max_delay:    upper bound for the backoff window.
        retryable:    exception types worth retrying; anything else
                      is re-raised immediately (fatal).
        sleep:        injectable for tests (default: time.sleep).
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except retryable as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        break
                    # Exponential window, then pick a random point
                    # inside it ("full jitter") so that many clients
                    # retrying the same server don't thunder-herd.
                    window = min(max_delay, base_delay * 2 ** (attempt - 1))
                    sleep(random.uniform(0, window))
            raise last_exc  # exhausted all attempts

        return wrapper

    return decorator


# --- Demo -----------------------------------------------------------------

# Deterministic demo: stub out sleep and the RNG for stable output.
sleeps = []


def fake_sleep(seconds):
    sleeps.append(round(seconds, 4))


# Use the worst-case point of each backoff window for stable output.
random.uniform = lambda a, b: b  # noqa: E731

call_log = []


def flaky_fetch(item_id: int) -> str:
    """Succeeds on the 3rd call; fails with ValueError before that.

    Raises TypeError (NOT in retryable) for negative ids — that
    failure must be fatal, not retried.
    """
    call_log.append(item_id)
    if item_id < 0:
        raise TypeError("negative id is a programming error")
    if len([c for c in call_log if c == item_id]) < 3:
        raise ValueError("simulated transient failure")
    return f"item-{item_id}"


# Apply the decorator manually so we can pass the fake sleep.
flaky_fetch = retry(
    max_attempts=4, base_delay=0.01, retryable=(ValueError,), sleep=fake_sleep
)(flaky_fetch)

print(flaky_fetch(7))       # -> item-7  (after 2 transient failures)
print("calls made:", len(call_log))   # -> 3
print("slept (s):", sleeps)           # -> [0.01, 0.02]

sleeps.clear()
try:
    flaky_fetch(-1)
except TypeError as exc:
    print(f"fatal error raised immediately: {exc}")
    print("calls made (no retry):", len(call_log))  # -> 4 (one fatal call)

# A function that never succeeds exhausts the budget:
attempts = []


@retry(max_attempts=3, base_delay=0.01, sleep=fake_sleep)
def always_fails():
    attempts.append(1)
    raise ConnectionError("network down")


try:
    always_fails()
except ConnectionError:
    print(f"gave up after {len(attempts)} attempts")  # -> 3
print("slept (s):", sleeps)  # -> [0.01, 0.02]
