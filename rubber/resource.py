import requests
from rubber import settings
from instanceutils import data_to_json

class Resource(object):
    def __init__(self, path, base_url=None, wrapper=None):
        self.path = path
        self.wrapper = wrapper or self._defaultwrapper

        if None == base_url:
            try:
                base_url = settings.ELASTICSEARCH_URL
            except AttributeError:
                pass

        if None == base_url:
            base_url = 'http://localhost:9200/'

        self.base_url = base_url

    def _defaultwrapper(self, response):
        return response

    def get(self, data=None, **kwargs):
        return self.wrapper(requests.get(self.base_url + self.path, data=data_to_json(data), **kwargs))

    def put(self, data=None, **kwargs):
        return self.wrapper(requests.put(self.base_url + self.path, data=data_to_json(data), **kwargs))

    def post(self, data=None, **kwargs):
        return self.wrapper(requests.post(self.base_url + self.path, data=data_to_json(data), **kwargs))

    def delete(self, data=None, **kwargs):
        return self.wrapper(requests.delete(self.base_url + self.path, data=data_to_json(data), **kwargs))

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

class InstanceResource(Resource):
    def __init__(self, instance, path, base_url=None, **kwargs):
        super(InstanceResource, self).__init__(path, base_url, **kwargs)
        self.instance = instance

    def post(self, **kwargs):
        return super(InstanceResource, self).post(data=self.instance, **kwargs)

    def put(self, **kwargs):
        return super(InstanceResource, self).put(data=self.instance, **kwargs)
