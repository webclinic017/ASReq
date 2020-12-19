import grequests as gr  # pip install grequests
from time import perf_counter  # Time measurement
import gachi_http as gh  # Library itself
import requests as r


def success(resp):  # Success handler to prove it's async
    print(resp)


reqs = [gh.get(f"https://google.com?i={i}") for i in range(10)]  # Get google 10 times with different parameter values
start = perf_counter()  # Start "stopwatch"
resp = gh.map(reqs, success_handler=success)  # Map request (execute)
print("GachiHTTP:", perf_counter() - start)  # Print time

start = perf_counter()
reqs = [r.get(f"https://google.com?i={i}") for i in range(10)]
print("Requests:", perf_counter() - start)

reqs = [gr.get(f"https://google.com?i={i}") for i in range(10)]
start = perf_counter()
gr.map(reqs)
print("GRequests:", perf_counter() - start)