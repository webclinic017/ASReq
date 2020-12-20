#!/usr/bin/env python3
from time import perf_counter  # Time measurement
import gachi_http as gh  # Library itself


def bad(a, b):
    print(a, b)


def success(resp):  # Success handler to prove it's async
    print(resp)


reqs = [gh.get(f"https://ya.ru?i={i}") for i in range(10)]  # Get google 10 times with different parameter values
start = perf_counter()  # Start "stopwatch"
resp = gh.map(reqs)  # Map request (execute)
print("GachiHTTP:", perf_counter() - start)  # Print time
