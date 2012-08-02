class Hit(object):
    def __init__(self, dict_response):
        self.attributes = {}
        for key, val in dict_response.items():
            if isinstance(val, dict):
                self.attributes[key] = Hit(val)
            elif isinstance(val, list):
                self.attributes[key] = [Hit(o) for o in val]
            else:
                self.attributes[key] = val

    def __getattribute__(self, name):
        default_impl = super(Hit, self).__getattribute__
        attributes = default_impl('attributes')
        if attributes.has_key(name):
            return attributes.get(name)
        if not name.startswith('_') and attributes.has_key("_%s"%name):
            return attributes.get("_%s"%name)
        return default_impl(name)
    
class Response(object):
    def __init__(self, dict_response, hit_class=Hit):
        self.took = dict_response.get('took')
        self.timed_out = dict_response.get('timed_out')
        self.hits = HitCollection(dict_response.get('hits'), hit_class=hit_class)
        self.shards = Shard(dict_response.get('_shards'))

class Shard(object):
    def __init__(self, dict_response):
        dict_response = dict_response or {}
        self.total = dict_response.get('total')
        self.successful = dict_response.get('successful')
        self.failed = dict_response.get('failed')

class HitCollection(object):
    def __init__(self, dict_response, hit_class=Hit):
        dict_response = dict_response or {}
        self.total = dict_response.get('total')
        self.max_score = dict_response.get('max_score')
        self.hits = []
        for hit_dict in dict_response.get('hits', []):
            self.hits.append(hit_class(hit_dict))

    def __len__(self):
        return len(self.hits)

    def __getitem__(self, i):
        return self.hits[i]
