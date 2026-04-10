from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timer():
    start = perf_counter()
    payload = {"elapsed_s": None}
    try:
        yield payload
    finally:
        payload["elapsed_s"] = perf_counter() - start
