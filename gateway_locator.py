"""
Parse data from Urs' Gateway Locator
https://github.com/urs8000/LoRa-Gateway-Locator
"""

import operator
from functools import reduce


def dms2decimal(degrees, minutes, seconds):
    op = operator.__add__ if degrees >= 0 else operator.__sub__
    return reduce(op, [degrees, float(minutes)/60, float(seconds)/3600])


def parse_coords(data_point):
    if 'data_plain' not in data_point:
        raise ValueError('Invalid GPS data')

    # Convert raw coordinate encoding into DMS and then decimal
    raw = data_point['data_plain']
    lat = dms2decimal(int(raw[0:2]), int(raw[2:4]) + int(raw[4:7])/1000, 0)
    lon = dms2decimal(int(raw[7:8]), int(raw[8:10]) + int(raw[10:])/1000, 0)

    return (lon, lat)
