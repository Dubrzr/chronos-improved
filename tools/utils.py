from codecs import getreader
from concurrent.futures import ThreadPoolExecutor, as_completed
from json import load as json_load
from urllib.request import urlopen

from chronos.settings import ASYNC_MAX_WORKERS


def request(url):
    print('Requesting {} ...'.format(url))
    response = urlopen(url)
    reader = getreader("utf-8")
    return reader(response)


def request_json(url):
    return json_load(request(url))


def async_requests(urls):
    result = {}
    with ThreadPoolExecutor(max_workers=ASYNC_MAX_WORKERS) as executor:
        fs = { executor.submit(request_json, url): url for url in urls }
        for future in as_completed(fs): # yield as soon as completed
            url = fs[future]
            try:
                data = future.result()
                result[url] = data
            except Exception:
                result[url] = None
    return result