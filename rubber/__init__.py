
try:
    from django.conf import settings
except:
    class _settings:
        ELASTICSEARCH_URL = None
        RUBBER_DISABLE_AUTO_INDEX = False

    settings = _settings()

from rubber.resource import Resource
from rubber.client import ElasticSearch
