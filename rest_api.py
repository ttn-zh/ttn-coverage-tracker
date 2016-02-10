import requests

import logging
import hashlib

ENCODING = 'utf-8'
NODE_API_URL = 'http://thethingsnetwork.org/api/v0/nodes/%s/?offset=%d'
GATEWAY_API_URL = 'http://thethingsnetwork.org/api/v0/gateways/%s/?limit=1'

logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)


def fetch_data_points(node_eui, offset):
    logger.info('Requesting API data [%d..%d]', offset, offset + 100)
    api_url = NODE_API_URL % (node_eui, offset)

    r = requests.get(api_url)
    if r.status_code != 200:
        logger.error('API request failed, HTTP Status: %d', r.status_code)
        sys.exit()

    r.encoding = ENCODING

    json_result = r.json()

    for data_point in json_result:
        id = data_point['time'] + data_point['gateway_eui']
        data_point['hash'] = hashlib.sha1(id.encode(ENCODING)).hexdigest()

        yield data_point


def fetch_gateway(gateway_eui):
    logger.info('Requesting Gateway API [%s]', gateway_eui)
    api_url = GATEWAY_API_URL % gateway_eui

    r = requests.get(api_url)
    if r.status_code != 200:
        logger.error('API request failed, HTTP Status: %d', r.status_code)
        sys.exit()

    r.encoding = ENCODING

    status_packets = r.json()

    return status_packets[0]
