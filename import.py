#!/usr/bin/env python3

import rest_api
import features

import logging
import coloredlogs
import argparse
import time

MAX_API_CALLS = 10

logger = logging.getLogger(__name__)


def import_new_features(node_eui, exclude_list, geojson_file):
    features_by_node = features.load(geojson_file)
    features_by_gateway = []
    feature_hashes = set([x['properties']['hash'] for x in features_by_node])

    def exists_predicate(data):
        return data['properties']['hash'] in feature_hashes

    for feature in get_new_geojson_features(node_eui, exists_predicate):
        gateway_eui = feature['properties']['gateway_eui']
        if gateway_eui in exclude_list:
            continue

        features_by_node.append(feature)
        feature_hashes.add(feature['properties']['hash'])

    features.dump(geojson_file, features_by_node)


def get_new_geojson_features(node_eui, already_exists_predicate):
    offset = 0
    api_calls = 0

    while True:
        api_calls += 1
        api_result = rest_api.fetch_data_points(node_eui, offset)

        count = 0
        for data_point in api_result:
            try:
                count += 1
                feature = features.build(data_point)
                if already_exists_predicate(feature):
                    logger.info('Found last imported data point, stopping.')
                    return

                print('.', end='')
                yield feature
            except:
                print('x', end='')

        if count == 0:
            logger.info('Reached end of data stream.')
            return

        print('')
        if api_calls >= MAX_API_CALLS:
            logger.error('Exceeded the max numbers of API calls, aborting.')
            return

        logger.info('Giving a break to the API server...')
        time.sleep(10)
        offset += 100


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('node_eui', help='Identifier of the node to import')
    parser.add_argument('-x', '--exclude', action='append', default=[],
                        help='Exclude gateways, multiple gateway EUIs allowed')

    return parser.parse_args()


def main():
    args = parse_args()

    loglevel = logging.INFO if args.verbose is None else logging.DEBUG
    logging.basicConfig(level=loglevel)
    coloredlogs.install()

    node_eui = args.node_eui

    geojson_file = 'maps/%s.json' % node_eui
    import_new_features(node_eui, args.exclude, geojson_file)


if __name__ == "__main__":
    main()
