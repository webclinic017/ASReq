import asyncio
from aiohttp import ClientSession, ClientTimeout
from ssl import create_default_context, SSLContext
from json import loads
from aiohttp_socks import ProxyConnector
from threading import Thread, currentThread
from typing import List, Optional, Union, Any, Dict


class Response:
    def __init__(self, url: str, status: int, headers: dict, content: Optional[bytes] = None):
        """
        Response class used after the request was made to make the response look like a requests-library response

        :param url: Url request was made to (may be used for debugging)
        :param status: Status code
        :param headers: Response headers
        :param content: Bytes-Content if include_content was set
        """
        self.url = url
        self.status_code = status
        self.content = content
        self.text = None
        if self.content is not None:
            self.text = self.content.decode("latin1")
        self.headers = {}
        for h in headers.keys():  # Convert aiohttp headers into beloved dict
            val = headers[h]
            self.headers[h] = val

    def json(self) -> dict:
        """
        Load the response text and convert it into json

        :return: JSON Object as dict
        """
        return loads(self.text)

    def __repr__(self) -> str:
        """
        Representation of a Response object when simply printing it out

        :return: <Response STATUS ["URL"]>
        """
        return f'<Response {self.status_code} ["{self.url}"]>'


class ThreadExecutor:
    def __init__(self):
        """
        ThreadExecutor allows a thread to be monitored and its data to be stored (the thread passes data to
          the object and then ends). Used in mapThreaded() function. There might be a better working solution for
          threaded execution with data saving, but this also works
        """
        self.status = "not_started"
        self.data = None
        self.thread = None

    def start(self) -> bool:
        """
        Start ThreadExecutor and get current thread to monitor

        :return: (Un)success
        """
        if self.status != "not_started":
            return False
        self.thread = currentThread()  # Current thread to monitor
        self.status = "running"
        return True

    def set_data(self, data: Any):
        """
        Set thread return data

        :param data: Data to set
        """
        self.data = data

    def finished(self) -> Dict[bool, Any]:
        """
        Check if the execution has finished

        :return: {Finished (True/False), data}
        """
        if self.status != "running":
            return {'finished': False}
        elif self.thread.is_alive():
            return {'finished': False}
        self.thread = None
        self.status = "not_started"
        return {'finished': True, 'data': self.data}

    def __repr__(self):
        """
        Representation of a ThreadExecutor object when simply printing it out

        :return: <Thread [STATUS]>
        """
        return f'Thread [{self.status.upper()}]'


class Request:
    def __init__(self, method: str, url: str, params: Union[dict, tuple], data: Union[dict, tuple, str],
                 json: Optional[dict], headers: Optional[dict], proxies: Union[dict, str],
                 skip_headers: Optional[list]):
        """
        Request class(es) getting passed to map() function

        :param method: Request method
        :param url: URL to request
        :param params: Query params to add to url
        :param headers: Headers as dict
        :param proxies: Proxies as dict or string
        :param data: POST data as dict (Content-Type: urlencoded) or string (Content-Type: text/plain)
        :param json: JSON POST data (Content-Type: application/json)
        :param skip_headers: Set automatically. Which headers not to generate automatically
        """
        self.method = method
        self.url = url
        self.params = params
        self.data = data
        self.json = json
        self.headers = headers
        self.proxies = proxies
        self.skip_headers = skip_headers

    def __repr__(self):
        """
        Representation of a request object when simply printing it out

        :return: <Request [METHOD "URL"]>
        """
        return f'<Request [{self.method} "{self.url}"]>'


def __startswith(word: str, _list: list) -> bool:
    """
    Check whether the word starts with one of specified words or not. Needed for proxy type identification

    :param word: Word to search in
    :param _list: List of strings word should start with
    :return: Whether the word starts with one of them or not
    """
    starts = False
    for w in _list:
        if word.startswith(w):
            starts = True
            break
    return starts


def request(method: str, url: str, params: Union[dict, tuple] = None, data: Union[dict, str] = None,
            json: Optional[dict] = None,
            headers: Optional[dict] = None, proxies: Union[dict, str] = None,
            skip_headers: Optional[list] = None) -> Union[Response, None]:
    """
    Create a Request with specified method and parameters. Used by many methods in this lib

    :param method: Request method
    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :param data: POST data as dict (Content-Type: urlencoded) or string (Content-Type: text/plain)
    :param json: JSON POST data (Content-Type: application/json)
    :param skip_headers: Set automatically. Which headers not to generate automatically
    :return: Request object
    """
    if skip_headers is None:
        skip_headers = []  # Mutable object, can't be set to list by default as parameter, must be done here
    if data is None and json is None:
        skip_headers.append('Content-Type')  # Otherwise "octet-stream" content type would be set
    if method.upper() not in ['POST', 'GET', 'PUT', 'HEAD', 'OPTIONS', 'DELETE', 'PATCH']:
        return None
    if proxies is not None:
        if isinstance(proxies, dict):  # Format: {'https': 'socks4(5)://...' or 'https://...'}
            proxies = list(proxies.values())[0]  # Get the first value -> only the proxy string
        if not __startswith(proxies, ['http', 'https', 'socks4', 'socks5']):
            proxies = None
        else:
            proxies = ProxyConnector.from_url(proxies)
    return Request(method.upper(), url, params, data, json, headers, proxies, skip_headers)


def get(url: str, params: Union[dict, tuple] = None, headers: Optional[dict] = None,
        proxies: Union[dict, str] = None) -> Request:
    """
    HTTP GET Method. Generates and returns a Request object

    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :return: Request object
    """
    return request('GET', url=url, params=params, headers=headers, proxies=proxies)


def head(url: str, params: Union[dict, tuple] = None, headers: Optional[dict] = None,
         proxies: Union[dict, str] = None) -> Request:
    """
    HTTP HEAD Method. Generates and returns a Request object

    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :return: Request object
    """
    return request('HEAD', url=url, params=params, headers=headers, proxies=proxies)


def options(url: str, params: Union[dict, tuple] = None, headers: Optional[dict] = None,
            proxies: Union[dict, str] = None) -> Request:
    """
    HTTP OPTIONS Method. Generates and returns a Request object

    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :return: Request object
    """
    return request('OPTIONS', url=url, params=params, headers=headers, proxies=proxies)


def delete(url: str, params: Union[dict, tuple] = None, headers: Optional[dict] = None,
           proxies: Union[dict, str] = None) -> Request:
    """
    HTTP DELETE Method. Generates and returns a Request object

    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :return: Request object
    """
    return request('DELETE', url=url, params=params, headers=headers, proxies=proxies)


def post(url: str, params: Union[dict, tuple] = None, data: Union[dict, str] = None, json: Optional[dict] = None,
         headers: Optional[dict] = None, proxies: Union[dict, str] = None) -> Request:
    """
    HTTP POST Method. Generates and returns a Request object

    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :param data: POST data as dict (Content-Type: urlencoded) or string (Content-Type: text/plain)
    :param json: JSON POST data (Content-Type: application/json)
    :return: Request object
    """
    return request('POST', url=url, params=params, data=data, json=json, headers=headers, proxies=proxies)


def patch(url: str, params: Union[dict, tuple] = None, data: Union[dict, str] = None, json: Optional[dict] = None,
          headers: Optional[dict] = None, proxies: Union[dict, str] = None) -> Request:
    """
    HTTP PATCH Method. Generates and returns a Request object

    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :param data: PATCH data as dict (Content-Type: urlencoded) or string (Content-Type: text/plain)
    :param json: JSON PATCH data (Content-Type: application/json)
    :return: Request object
    """
    return request('PATCH', url=url, params=params, data=data, json=json, headers=headers, proxies=proxies)


def put(url: str, params: Union[dict, tuple] = None, data: Union[dict, str] = None, json: Optional[dict] = None,
        headers: Optional[dict] = None, proxies: Union[dict, str] = None) -> Request:
    """
    HTTP PUT Method. Generates and returns a Request object

    :param url: URL to request
    :param params: Query params to add to url
    :param headers: Headers as dict
    :param proxies: Proxies as dict or string
    :param data: PUT data as dict (Content-Type: urlencoded) or string (Content-Type: text/plain)
    :param json: JSON PUT data (Content-Type: application/json)
    :return: Request object
    """
    return request('PUT', url=url, params=params, data=data, json=json, headers=headers, proxies=proxies)


async def __exec_req(sem: asyncio.Semaphore, sess: ClientSession, req: Request, ssl: SSLContext, include_content: bool,
                     exception_handler, success_handler) -> Response:
    """
    Executes one request asynchronously. When used in asyncio.gather() makes requests go really fast.
    Do not use it yourself. Use map() instead

    :param sem: asyncio.Semaphore to avoid "Too many open files" Exception and allow the user to set number of
     concurrent connections
    :param sess: aiohttp.ClientSession() to make requests with
    :param req: Request object
    :param ssl: Generated SSL context
    :param include_content: Whether include response content (+decoded Text) or not
    :param exception_handler: Function to report a failed (with exceptions) response (passes exception as parameter)
    :param success_handler: Function to report a succeeded (with no exceptions) response (passes Response object as
     parameter)
    :return: Response object
    """
    try:
        async with sem, sess.request(method=req.method, url=req.url, params=req.params, data=req.data, json=req.json,
                                     headers=req.headers,
                                     proxy=req.proxies, skip_auto_headers=req.skip_headers, ssl=ssl) as resp:
            # Semaphore used to control amount of connections per once. Make request and perform actions
            content = None
            if include_content:
                content = await resp.read()  # Read thr content
            final = Response(req.url, resp.status, resp.headers, content)  # Generate the response
            if success_handler is not None:  # Success handler report
                Thread(target=success_handler, args=[final]).start()  # Because we don't know what success handler
                # will do, it might block the further execution -> use external Thread to start it
            return final
    except Exception as e:
        if exception_handler is not None:
            Thread(target=exception_handler, args=[e]).start()


async def __make_reqs(reqs: List[Request], size: int, timeout: Optional[int], include_content: bool, exception_handler,
                      success_handler) -> List[Response]:
    """
    Asynchronous runner for map() function. Do not start it yourself, use map() instead

    :param reqs: List with Request objects. Use different methods to create them
    :param size: Connections per once. Might affect some website-security (nginx) against you
    :param timeout: Connection timeout
    :param include_content:
    :param exception_handler: Function to report a failed (with exceptions) response (passes exception as parameter)
    :param success_handler: Function to report a succeeded (with no exceptions) response (passes Response object as
      parameter)
    :return: List with Response objects
    """
    sem = asyncio.Semaphore(size)  # Usage in __execReq()
    ssl = create_default_context()  # Create SSL Context
    async with ClientSession(timeout=ClientTimeout(total=timeout)) as sess:  # Create requests session
        fut = asyncio.gather(
            *[asyncio.ensure_future(
                __exec_req(sem, sess, req, ssl, include_content, exception_handler, success_handler))
                for req in reqs])  # Create a task for each request
        resp = await fut  # Asynchronously execute them
    return resp  # Return Response objects


def map(reqs: List[Request], size: Optional[int] = 10, timeout: Optional[int] = None,
        include_content: Optional[bool] = True,
        exception_handler=None, success_handler=None) -> List[Response]:
    """
    Map (start) asynchronous requests and get a list of responses

    :param reqs: List with Request objects. Use different methods to create them
    :param size: Connections per once. Might affect some website-security (nginx) against you
    :param timeout: Connection timeout
    :param include_content: Whether include response content (+decoded Text) or not
    :param exception_handler: Function to report a failed (with exceptions) response (passes exception as parameter)
    :param success_handler: Function to report a succeeded (with no exceptions) response (passes Response object as
      parameter)
    :return: List with Response objects
    """
    valid_reqs = []
    for req in reqs:  # Go through each request and sort out None(s) and empty URLs
        if req is None or not req.url:
            continue
        valid_reqs.append(req)
    loop = asyncio.new_event_loop()  # As this function might be used in separate Thread, we have to create a new loop
    # for each one
    asyncio.set_event_loop(loop)  # Set new loop for current thread
    fut = asyncio.gather(asyncio.ensure_future(
        __make_reqs(valid_reqs, size, timeout, include_content, exception_handler, success_handler)))  # Start
    # asynchronous execution
    resp = loop.run_until_complete(fut)
    loop.close()
    return resp[0]  # Format [[Response, Response...]], this is why we return resp[0] -> only the Responses


def __threaded(executor: ThreadExecutor, reqs, size, timeout, include_content, exception_handler,
               success_handler) -> None:
    """
    Thread runner for mapThreaded(). Do not use yourself, use mapThreaded() instead

    :param executor: ThreadExecutor to report status and set data in
    :param reqs: List with Request objects. Use different methods to create them
    :param size: Connections per once. Might affect some website-security (nginx) against you
    :param timeout: Connection timeout
    :param include_content: Whether include response content (+decoded Text) or not
    :param exception_handler: Function to report a failed (with exceptions) response (passes exception as parameter)
    :param success_handler: Function to report a succeeded (with no exceptions) response (passes Response object as
      parameter)
    """
    executor.start()  # Let the executor know who he deals with
    resp = map(reqs, size, timeout, include_content, exception_handler, success_handler)  # Map requests in separate
    # thread
    executor.set_data(resp)  # Set data for return and exit


def map_threaded(reqs: List[Request], size: Optional[int] = 10, timeout: Optional[int] = None,
                include_content: Optional[bool] = True,
                exception_handler=None, success_handler=None) -> ThreadExecutor:
    """
    Threaded execution of asynchronous requests. Returns a ThreadExecutor

    :param reqs: List with Request objects. Use different methods to create them
    :param size: Connections per once. Might affect some website-security (nginx) against you
    :param timeout: Connection timeout
    :param include_content: Whether include response content (+decoded Text) or not
    :param exception_handler: Function to report a failed (with exceptions) response (passes exception as parameter)
    :param success_handler: Function to report a succeeded (with no exceptions) response (passes Response object as
      parameter)
    :return: ThreadExecutor
    """
    executor = ThreadExecutor()
    t = Thread(target=__threaded,
               args=[executor, reqs, size, timeout, include_content, exception_handler, success_handler])
    t.start()
    return executor
