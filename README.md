# GachiHTTP

Asynchronous requests library based on aiohttp and has grequests syntax

## Advantages

* Thread safe (compared to gevent-based `grequests`)
* Fast (about 8.5x faster than `requests`)
* Easy-to-use (same syntax as in `grequests`, really similar to `requests`)

## Installation

> pip install gachi_http

## Basic usage

```python
from time import perf_counter  # Time measurement
import gachi_http as gh  # Library itself


def success(resp):  # Success handler to prove it's async
    print(resp)


reqs = [gh.get(f"https://google.com?i={i}") for i in range(10)]  # Get google 10 times with different parameter values
start = perf_counter()  # Start "stopwatch"
resp = gh.map(reqs, success_handler=success)  # Map request (execute)
print("Time:", perf_counter() - start)  # Print time
```

#### Example output

```python
<Response 200 ["https://google.com?i=5"]>
<Response 200 ["https://google.com?i=6"]>
<Response 200 ["https://google.com?i=4"]>
<Response 200 ["https://google.com?i=8"]>
<Response 200 ["https://google.com?i=0"]>
<Response 200 ["https://google.com?i=3"]>
<Response 200 ["https://google.com?i=9"]>
<Response 200 ["https://google.com?i=1"]>
<Response 200 ["https://google.com?i=2"]>
<Response 200 ["https://google.com?i=7"]>
Time: 0.351634674
```

## Methods

Method | Description | Returns
------ | ----------- | -------
`request (method, url, params, headers, proxies, data, json, skip_headers)` | Create a Request with specified method and parameters. Used by many methods in this lib | `Request` object
`get(url, params, headers, proxies)` | HTTP GET Method. Generates and returns a Request object | `Request` object
`post(url, params, headers, data, json)` | HTTP POST Method. Generates and returns a Request object | `Request` object
`head`, `options`, `put`, `delete`, `patch` | Other HTTP methods. Parameters available in docstring | `Request` object
`map(reqs, size, timeout, include_content, exception_handler, success_handler, verify_ssl)` | Map (start) asynchronous requests and get a list of responses | List with `Response` objects
`map_threaded(reqs, size, timeout, include_content, exception_handler, success_handler, verify_ssl, finished_handler)` | Threaded execution of asynchronous requests. Returns a ThreadExecutor | `ThreadExecutor` object

#### Response class attributes

* `status_code` - Response status code
* `url` - URL Request was mad to. For debugging purposes
* `content` - Bytes-response if include_content was set
* `text` - Decoded `content`
* `headers` - Response headers as dict
* `json()` - Convert response text into JSON dict

####ThreadExecutor class methods

* `finished()` - Check whether the thread has finished or not. Returns a dict: `{'finished': True/False(, 'data': List[Responses])}`

## Further documentation available in docstrings of the library!!!
