import requests
import json
from rubber import settings
from instanceutils import data_to_json

class Resource(object):
    def __init__(self, path, base_url=None, wrapper=None):
        self.path = path
        self.wrapper = wrapper or dict

        if None == base_url:
            try:
                base_url = settings.ELASTICSEARCH_URL
            except AttributeError:
                pass

        if None == base_url:
            base_url = 'http://localhost:9200/'

        self.base_url = base_url

    def get(self, data=None, **kwargs):
        return self.wrapper(json.loads(requests.get(self.base_url + self.path, data=data_to_json(data), **kwargs).content))

    def put(self, data=None, **kwargs):
        return self.wrapper(json.loads(requests.put(self.base_url + self.path, data=data_to_json(data), **kwargs).content))

    def post(self, data=None, **kwargs):
        return self.wrapper(json.loads(requests.post(self.base_url + self.path, data=data_to_json(data), **kwargs).content))

    def delete(self, data=None, **kwargs):
        return self.wrapper(json.loads(requests.delete(self.base_url + self.path, data=data_to_json(data), **kwargs).content))

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
