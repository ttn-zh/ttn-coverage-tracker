#!/usr/bin/env python3

from coverage_map import CoverageMap

import rest_api
import features

import logging
import coloredlogs
import argparse
import time

MAX_API_CALLS = 50

logger = logging.getLogger(__name__)


def import_new_features(node_eui, exclude_list):
    coverage = CoverageMap(node_eui)

    for feature in get_new_features(node_eui, exclude_list):
        if coverage.exists(feature):
            logger.info('Found last imported data point, stopping.')
            break
        coverage.add(feature)

    coverage.save_all()


def get_new_features(node_eui, exclude_list):
    offset = 0
    api_calls = 0

    while True:
        api_calls += 1
        api_result = rest_api.fetch_data_points(node_eui, offset)

        count = 0
        for data_point in api_result:
            try:
                count += 1

                if data_point['gateway_eui'] in exclude_list:
                    continue

                feature = features.build(data_point)

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

    import_new_features(args.node_eui, args.exclude)


if __name__ == "__main__":
    main()
