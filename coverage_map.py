import features


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
