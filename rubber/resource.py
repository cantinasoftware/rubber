import requests
from rubber import settings
from rubber.testutils import ResponseMock
from instanceutils import data_to_json

class Resource(object):
    def __init__(self, path, base_url=None, wrapper=None, raise_on_error=False):
        self.path = path
        self.wrapper = wrapper or self._defaultwrapper

        if None == base_url:
            try:
                base_url = settings.RUBBER_ELASTICSEARCH_URL
            except AttributeError:
                pass

        if None == base_url:
            base_url = 'http://localhost:9200/'

        self.base_url = base_url
        self.raise_on_error = raise_on_error

    def _defaultwrapper(self, response):
        return response

    def request(self, method, data=None, **kwargs):
        if getattr(settings, 'RUBBER_MOCK_HTTP_RESPONSE', False):
            return self.wrapper(ResponseMock(settings.RUBBER_MOCK_HTTP_RESPONSE))
        path = self.base_url + self.path
        try:
            response = requests.request(method, path, data=data_to_json(data), **kwargs)
        except Exception, e:
            if self.raise_on_error:
                raise
            import logging
            logging.exception('Could not perform %s %s' % (method.upper(), path))
            return None
        return self.wrapper(response)

    def get(self, data=None, **kwargs):
        return self.request('GET', data=data, **kwargs)

    def put(self, data=None, **kwargs):
        return self.request('PUT', data=data, **kwargs)

    def post(self, data=None, **kwargs):
        return self.request('POST', data=data, **kwargs)

    def delete(self, data=None, **kwargs):
        return self.request('DELETE', data=data, **kwargs)

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
