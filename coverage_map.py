import features


class CoverageMap:
    def __init__(self, node_eui):
        self.file = 'maps/%s.json' % node_eui
        self.features = features.load(self.file)
        self.hashes = set([x['properties']['hash'] for x in self.features])
        self.gateways = {}

    def exists(self, data):
        return data['properties']['hash'] in self.hashes

    def add(self, feature):
        eui = feature['properties']['gateway_eui']

        if eui not in self.gateways:
            self.gateways[eui] = features.load('maps/%s.json' % eui)

        self.features.append(feature)
        self.hashes.add(feature['properties']['hash'])
        self.gateways[eui].append(feature)

    def save_all(self):
        features.dump(self.file, self.features)

        for eui in self.gateways:
            features.dump('maps/%s.json' % eui, self.gateways[eui])
