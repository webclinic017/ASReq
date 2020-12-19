from time import perf_counter  # Time measurement
import gachi_http as gh  # Library itself


def bad(a, b):
    print(a, b)


def success(resp):  # Success handler to prove it's async
    print(resp)


prx = "socks5://3405kp:0u45dM@194.124.49.104:8000"

reqs = [gh.get(f"https://ya.ru?i={i}") for i in range(10)]  # Get google 10 times with different parameter values
start = perf_counter()  # Start "stopwatch"
resp = gh.map(reqs, proxies=prx)  # Map request (execute)
print("GachiHTTP:", perf_counter() - start)  # Print time
