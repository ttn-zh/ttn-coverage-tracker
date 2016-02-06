import parser

import geojson
import os.path

gateway_marker_symbols = {}


def build(data_point):
    coords = parser.get_coords(data_point)
    if coords is None:
        raise ValueError("No GPS data")

    point = geojson.Point(coords)
    props = dict(hash=data_point['hash'], time=data_point['time'],
                 gateway_eui=data_point['gateway_eui'], snr=data_point['snr'],
                 rssi=data_point['rssi'], data_rate=data_point['datarate'])

    # Add styling features
    # https://help.github.com/articles/mapping-geojson-files-on-github/
    props['marker-symbol'] = get_marker_symbol(data_point)
    props['marker-color'] = get_marker_color(data_point)

    return geojson.Feature(geometry=point, properties=props)


def get_marker_symbol(data_point):
    eui = data_point['gateway_eui']
    if eui in gateway_marker_symbols:
        return gateway_marker_symbols[eui]

    symbol = chr(len(gateway_marker_symbols) + 97)
    gateway_marker_symbols[eui] = symbol

    return symbol


def get_marker_color(data_point):
    color = '#7d8182'  # default to grey

    try:
        rssi = float(data_point['rssi'])
    except:
        return color

    if rssi < 0 and rssi >= -70:
        color = '#005a32'
    if rssi < -70:
        color = '#238443'
    if rssi < -90:
        color = '#41ab5d'
    if rssi < -100:
        color = '#78c679'
    if rssi < -110:
        color = '#addd8e'
    if rssi < -115:
        color = '#d9f0a3'

    return color


def load(filename):
    if not os.path.isfile(filename):
        return []

    collection = geojson.loads(open(filename, 'r').read())
    return collection.features


def dump(filename, features):
    geojson_file = open(filename, 'w')
    geojson_file.write(geojson.dumps(geojson.FeatureCollection(features),
                       indent=4, sort_keys=True))
