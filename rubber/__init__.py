
try:
    from django.conf import settings
except:
    class _settings:
        ELASTICSEARCH_URL = None
    settings = _settings()

from rubber.resource import Resource
from rubber.client import ElasticSearch
