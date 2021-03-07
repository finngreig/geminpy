import re
from .request import Request

# matches hostname and subsequent path
REQUEST_PATTERN = r"gemini://([^/]+)(/.*)*\r\n"


def parse_request(data):
    data_string = data.decode('utf-8')
    match = re.match(REQUEST_PATTERN, data_string)

    if match is None:
        return None

    (hostname, path) = match.groups()

    return Request(hostname, path)
