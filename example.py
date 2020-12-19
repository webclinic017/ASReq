from time import perf_counter  # Time measurement
import gachi_http as gh  # Library itself


def success(resp):  # Success handler to prove it's async
    print(resp)


reqs = [gh.get(f"https://google.com?i={i}") for i in range(10)]  # Get google 10 times with different parameter values
start = perf_counter()  # Start "stopwatch"
resp = gh.map(reqs, success_handler=success)  # Map request (execute)
print("Time:", perf_counter() - start)  # Print time

# Example output:
# <Response 200 ["https://google.com?i=5"]>
# <Response 200 ["https://google.com?i=6"]>
# <Response 200 ["https://google.com?i=4"]>
# <Response 200 ["https://google.com?i=8"]>
# <Response 200 ["https://google.com?i=0"]>
# <Response 200 ["https://google.com?i=3"]>
# <Response 200 ["https://google.com?i=9"]>
# <Response 200 ["https://google.com?i=1"]>
# <Response 200 ["https://google.com?i=2"]>
# <Response 200 ["https://google.com?i=7"]>
# Time: 0.351634674
