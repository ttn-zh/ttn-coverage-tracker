#!/usr/bin/env python3

import geojson
import requests
import sys, getopt, hashlib, time, operator, os.path
from functools import reduce

API_ENCODING = 'utf-8'
MAX_API_CALLS = 10

def usage():
    return 'usage: %s <node_eui>' % sys.argv[0]

def main(argv):
    node_eui = None

    try:
        opts, args = getopt.getopt(argv,"h",["help"])
    except getopt.GetoptError:
        print(usage())
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage())
            sys.exit()

    if len(args) > 0:
        node_eui = args[0]

    if node_eui is None:
        print(usage())
        sys.exit(2)

    geojson_file = '%s.json' % node_eui
    import_new_features(node_eui, geojson_file)


def import_new_features(node_eui, geojson_file):
    feature_hashes = load_features(geojson_file)
    features = []

    for feature in get_new_geojson_features(node_eui, lambda x : x['properties']['hash'] in feature_hashes):
        gateway_eui = feature['properties']['gateway_eui']

        features.append(feature)
        feature_hashes.add(feature['properties']['hash'])

        print('.', end='')

    geojson_file = open(geojson_file, 'w')
    geojson_file.write(geojson.dumps(geojson.FeatureCollection(features), indent=4, sort_keys=True))

def load_features(geojson_file):
    if not os.path.isfile(geojson_file):
        return set()

    collection = geojson.loads(open(geojson_file, 'r').read())
    return set([x['properties']['hash'] for x in collection.features])

def get_new_geojson_features(node_eui, already_exists_predicate):
    offset = 0
    api_calls = 0

    while True:
        api_calls += 1
        api_result = fetch_data_points(node_eui, offset)

        if len(api_result) == 0:
            print('Found end of node data stream')
            return

        for data_point in api_result:
            try:
                feature = geojson_feature(data_point)
                if already_exists_predicate(feature):
                    return

                yield feature
            except:
                print('x', end='')
                # print("Failed to parse data point %s" % data_point)

        print('')
        if api_calls >= MAX_API_CALLS:
            print('Exceeded the max numbers of API calls, aborting...')
            return

        print('Giving a break to the API server...')
        time.sleep(10)
        offset += 100

def fetch_data_points(node_eui, offset):
    print('Requesting API data [%d..%d]' % (offset, offset + 100))
    api_url = 'http://thethingsnetwork.org/api/v0/nodes/%s/?offset=%d' % (node_eui, offset)

    r = requests.get(api_url)
    if r.status_code != 200:
        print('API request failed, HTTP Status: %d' % r.status_code)
        sys.exit()

    r.encoding = API_ENCODING

    return r.json()

def geojson_feature(data_point):
    data_point_id = (data_point['time'] + data_point['gateway_eui']).encode(API_ENCODING)
    data_point_hash = hashlib.sha1(data_point_id).hexdigest()

    # Convert raw coordinate encoding into DMS and then decimal
    raw_coords = data_point['data_plain']
    lat = dms2decimal(int(raw_coords[0:2]), int(raw_coords[2:4]) + int(raw_coords[4:7])/1000, 0)
    lon = dms2decimal(int(raw_coords[7:8]), int(raw_coords[8:10]) + int(raw_coords[10:])/1000, 0)

    point = geojson.Point((lon, lat))
    props = dict(hash=data_point_hash, gateway_eui=data_point['gateway_eui'], time=data_point['time'], rssi=data_point['rssi'], snr=data_point['snr'], data_rate=data_point['datarate'])

    return geojson.Feature(geometry=point, properties=props) 

def dms2decimal(degrees, minutes, seconds):
    op = operator.__add__ if degrees >= 0 else operator.__sub__
    return reduce(op, [degrees, float(minutes)/60, float(seconds)/3600])


if __name__ == "__main__":
   main(sys.argv[1:])
