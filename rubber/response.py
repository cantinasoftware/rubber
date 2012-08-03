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
    
import requests
class Response(object):
    """
    A HTTP response object that acts as a proxy on its provided requests.models.Response object
    """
    def __init__(self, response):
        self._response = response

    def __getattribute__(self, attr):
        if attr in ('_response', 'results'):
            return super(Response, self).__getattribute__(attr)
        return getattr(self._response, attr)

class SearchResponse(Response):
    def __init__(self, response, hit_class=Hit):
        super(SearchResponse, self).__init__(response)

        if self._response.json:
            self.results = HitCollection(self._response.json.get('hits'), hit_class=hit_class)
        else:
            self.results = HitCollection({})

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
