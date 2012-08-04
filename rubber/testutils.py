import requests

class ResponseMock(requests.models.Response):
    def __init__(self, content='{}'):
        super(ResponseMock, self).__init__()
        from StringIO import StringIO

        self.raw = StringIO(content)
        self.status_code = 200
        self._content = content
