import features
import math


def distance_on_km(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos(cos)
    return arc * 6373


class CoverageMap:
    def __init__(self, node_eui):
        self.file = 'maps/%s.json' % node_eui
        self.features = features.load(self.file)
        self.all_nodes = features.load('maps/all_nodes.json')
        self.hashes = set([x['properties']['hash'] for x in self.features])
        self.gateways = {}

        known_gateways = set([x['properties']['eui']
                             for x in self.all_nodes
                             if 'eui' in x['properties']])
        for eui in known_gateways:
            self.gateway_seen(eui)

    def exists(self, data):
        return data['properties']['hash'] in self.hashes

    def add(self, feature):
        eui = feature['properties']['gateway_eui']

        if eui not in self.gateways:
            raise ValueError('Unexpected error, gateway not found')

        gateway = self.gateways[eui][0]
        feature['properties']['marker-symbol'] = gateway['properties']['sym']
        lat1 = feature.geometry.coordinates[1]
        lon1 = feature.geometry.coordinates[0]
        lat2 = gateway.geometry.coordinates[1]
        lon2 = gateway.geometry.coordinates[0]
        distance = distance_on_km(lat1, lon1, lat2, lon2)

        feature['properties']['distance'] = "%.1f km" % distance

        self.features.append(feature)
        self.all_nodes.append(feature)
        self.hashes.add(feature['properties']['hash'])
        self.gateways[eui].append(feature)

    def save_all(self):
        features.dump(self.file, self.features)
        features.dump('maps/all_nodes.json', self.all_nodes)

        for eui in self.gateways:
            features.dump('maps/%s.json' % eui, self.gateways[eui])

    def gateway_seen(self, eui):
        if eui in self.gateways:
            return True

        self.gateways[eui] = features.load('maps/%s.json' % eui)

        return True if len(self.gateways[eui]) > 0 else False

    def add_gateway(self, feature):
        eui = feature['properties']['eui']
        feature['properties']['sym'] = chr(len(self.gateways) + 97)

        self.gateways[eui] = features.build_collection([feature]).features
        self.all_nodes.append(feature)
        self.features.append(feature)
