"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from unittest import TestCase
from rubber import Resource

import requests
from requests.compat import json

class ResponseMock(requests.models.Response):
    def __init__(self):
        super(ResponseMock, self).__init__()
        from StringIO import StringIO

        self.raw = StringIO(ResponseMock._content)
        self.status_code = 200

    _content = '{}'


class RequestMock(object):
    def __init__(self):
        self.stack = []
    def get(self, url, **kwargs):
        self.stack.append({'method': 'get', 'url':url, 'kwargs': kwargs})
        return ResponseMock()

    def put(self, url, **kwargs):
        self.stack.append({'method': 'put', 'url':url, 'kwargs': kwargs})
        return ResponseMock()

    def post(self, url, **kwargs):
        self.stack.append({'method': 'post', 'url':url, 'kwargs': kwargs})
        return ResponseMock()


class ResourceTest(TestCase):

    def test_base_url(self):
        """
        Tests that base_url defaults to settings['ELASTICSEARCH_URL'] or http://localhost:9200
        """
        import rubber

        setattr(rubber.settings, 'ELASTICSEARCH_URL', None)

        # Check there is a sensible default
        resource = rubber.Resource('/foo')
        self.assertEquals('http://localhost:9200/', resource.base_url)

        # Check that django settings are picked up
        rubber.settings.ELASTICSEARCH_URL = 'https://foo.com/'
        resource = rubber.Resource('/foo')
        self.assertEquals('https://foo.com/', resource.base_url)

        # Check that empty string can be set as base_url
        rubber.settings.ELASTICSEARCH_URL = ''
        resource = rubber.Resource('/foo')
        self.assertEquals('', resource.base_url)

    def test_data_to_json(self):
        """
        Tests that data_to_json serializes dicts / objects / models to json
        """

        from rubber.instanceutils import data_to_json

        # with a dict
        data = {'foo':'bar'}
        json_data = json.dumps(data)
        self.assertEquals(json_data, data_to_json(data))

        # with a string
        json_data = json.dumps(data)
        self.assertEquals(json_data, data_to_json(json_data))

        # try a class that implements to_indexed_json
        class Foo(object):
            def to_indexed_json(self):
                return json_data
        self.assertEquals(json_data, data_to_json(Foo()))

        # try a django model
        try:
            from django.db import models
            class TestModel(models.Model):
                foo = models.CharField(max_length=3)
            bar = TestModel(foo='bar')
            self.assertEquals(json_data, data_to_json(bar))
        except ImportError:
            pass

try:
    import django
    class ElasticSearchTest(TestCase):
        def setUp(self):
            import rubber
            setattr(rubber.settings, 'ELASTICSEARCH_URL', 'http://example.com:9200/')

            from django.db import models
            from rubber import ElasticSearch

            class Article(models.Model):
                elasticsearch = ElasticSearch(auto_index=True)

            self.Article = Article

        def test_contribute_to_class(self):
            """
            Checks that when set on a django model, index_name and type are automatically set
            to the app_name / model_name
            """
            self.assertEquals('tests', self.Article.elasticsearch.index_name)
            self.assertEquals('article', self.Article.elasticsearch.type)

        def test_search(self):
            """
            Checks that we call the right elasticsearch endpoint for searching
            """
            from rubber import resource
            requestmock = RequestMock()
            resource.requests = requestmock

            q = {'query': {'term': {'user': 'kimchy'}}}
            self.Article.elasticsearch.search(q, toto='titi')

            self.assertEquals(1, len(requestmock.stack))
            self.assertEquals('http://example.com:9200/tests/article/_search', requestmock.stack[0]['url'])
            self.assertEquals('get', requestmock.stack[0]['method'])
            self.assertEquals('titi', requestmock.stack[0]['kwargs']['toto'])
            from rubber.instanceutils import data_to_json
            self.assertEquals(data_to_json(q), requestmock.stack[0]['kwargs']['data'])

            self.Article.elasticsearch.mapping.put({'some': 'mapping'}, toto='titi')

            self.assertEquals(2, len(requestmock.stack))
            self.assertEquals('http://example.com:9200/tests/article/_mapping', requestmock.stack[1]['url'])
            self.assertEquals('put', requestmock.stack[1]['method'])
            self.assertEquals('titi', requestmock.stack[1]['kwargs']['toto'])

        def test_auto_index(self):
            """
            Check that the elasticsearch object is receiver for the post save / delete signals
            """
            from django.db.models.signals import post_save, post_delete
            from django.dispatch.dispatcher import _make_id
            import weakref
            for signal, callback in ((post_save, self.Article.elasticsearch.django_post_save), (post_delete, self.Article.elasticsearch.django_post_delete)):
                found = False
                for lookup_key, receiver in signal.receivers:
                    if lookup_key[0] == _make_id(callback):
                        found = True
                self.assertTrue(found)

        def test_instance(self):
            """
            Checks the .elasticsearch property of a model instance
            """
            article = self.Article()
            article.pk = 123

            # Check the article.elasticsearch property
            self.assertIsNotNone(article.elasticsearch)
            from rubber.resource import InstanceResource
            self.assertTrue(isinstance(article.elasticsearch, InstanceResource))
            self.assertEquals('tests/article/123', article.elasticsearch.path)
            
            from rubber import resource
            requestmock = RequestMock()
            resource.requests = requestmock

            # Check that put() passes the article instance as data
            article.elasticsearch.put()
            self.assertEquals(1, len(requestmock.stack))
            self.assertEquals("put", requestmock.stack[0]['method'])
            self.assertEquals('{}', requestmock.stack[0]['kwargs']['data'])

            # Check that post() passes the article instance as data
            article.elasticsearch.post()
            self.assertEquals(2, len(requestmock.stack))
            self.assertEquals("post", requestmock.stack[1]['method'])
            self.assertEquals('{}', requestmock.stack[1]['kwargs']['data'])

        def test_response(self):
            """
            Check that a Response object is returned
            """

            ResponseMock._content = """{"took":2,"timed_out":false,"_shards":{"total":5,"successful":5,"failed":0},"hits":{"total":2,"max_score":1.0,"hits":[{"_index":"auth","_type":"user","_id":"6","_score":1.0, "_source" : {"username": "guillaume", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T08:30:11", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$M1nRKJfbvdQf$ouX5u9FOUF/MKhhwuwYbiuoVidFITsBrEstGBB4mzZA=", "email": "somemail@test.com", "date_joined": "2012-08-02T08:30:11"}},{"_index":"auth","_type":"user","_id":"8","_score":1.0, "_source" : {"username": "stephane", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T09:14:38", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$ORDHZAnNqTwF$UGmkUCyH0/uh1ruP93ZSTyog9Wi5g2qc+m/fxowigFs=", "email": "othermail@test.com", "date_joined": "2012-08-02T09:14:38"}}]}}"""

            from rubber import resource
            requestmock = RequestMock()
            resource.requests = requestmock

            response = self.Article.elasticsearch.search({})
            
            self.assertEquals(2, response.json['took'])

            from rubber.response import Response
            self.assertTrue(isinstance(response, Response))

        def test_hit_class(self):
            """
            Checks that you can customize the hit_class
            """
            class MyHit(object):
                def __init__(self, d):
                    self.data = d

            self.Article.elasticsearch.hit_class = MyHit

            ResponseMock._content = """{"took":2,"timed_out":false,"_shards":{"total":5,"successful":5,"failed":0},"hits":{"total":2,"max_score":1.0,"hits":[{"_index":"auth","_type":"user","_id":"6","_score":1.0, "_source" : {"username": "guillaume", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T08:30:11", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$M1nRKJfbvdQf$ouX5u9FOUF/MKhhwuwYbiuoVidFITsBrEstGBB4mzZA=", "email": "somemail@test.com", "date_joined": "2012-08-02T08:30:11"}},{"_index":"auth","_type":"user","_id":"8","_score":1.0, "_source" : {"username": "stephane", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T09:14:38", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$ORDHZAnNqTwF$UGmkUCyH0/uh1ruP93ZSTyog9Wi5g2qc+m/fxowigFs=", "email": "othermail@test.com", "date_joined": "2012-08-02T09:14:38"}}]}}"""
            from rubber import resource
            requestmock = RequestMock()
            resource.requests = requestmock

            response = self.Article.elasticsearch.search({})

            # This should be a SearchResponse
            from rubber.response import SearchResponse
            self.assertTrue(isinstance(response, SearchResponse))

            # It should have a 'results' attribute
            self.assertTrue(hasattr(response, 'results'))

            # Hits should be MyHit objects
            self.assertTrue(isinstance(response.results.hits[0], MyHit))


except ImportError:
    pass

class HitCollectionTest(TestCase):
    def test_getitem_len_iter(self):
        """
        It should be possible to get its with bracket notation on collections, like collection[0], look at len(collection) and iterate for hit in collection.
        """

        response = json.loads("""{"took":2,"timed_out":false,"_shards":{"total":5,"successful":5,"failed":0},"hits":{"total":2,"max_score":1.0,"hits":[{"_index":"auth","_type":"user","_id":"6","_score":1.0, "_source" : {"username": "guillaume", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T08:30:11", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$M1nRKJfbvdQf$ouX5u9FOUF/MKhhwuwYbiuoVidFITsBrEstGBB4mzZA=", "email": "somemail@test.com", "date_joined": "2012-08-02T08:30:11"}},{"_index":"auth","_type":"user","_id":"8","_score":1.0, "_source" : {"username": "stephane", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T09:14:38", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$ORDHZAnNqTwF$UGmkUCyH0/uh1ruP93ZSTyog9Wi5g2qc+m/fxowigFs=", "email": "othermail@test.com", "date_joined": "2012-08-02T09:14:38"}}]}}""")
        from rubber.response import HitCollection
        collection = HitCollection(response['hits'])

        self.assertEquals(2, len(collection))
        self.assertEquals('guillaume', collection[0].source.username)
        self.assertEquals(['guillaume', 'stephane'], [hit.source.username for hit in collection])

class HitTest(TestCase):
    def test_init(self):
        from rubber.response import Hit
        data = {
            "_index" : "auth",
            "_type" : "user",
            "_id" : "6",
            "_score" : 0.054244425,
            "_source" : {"username": "guillaume", "first_name": "", "last_name": "", "is_active": True, "is_superuser": False, "is_staff": False, "last_login": "2012-08-02T08:30:11.562", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$M1nRKJfbvdQf$ouX5u9FOUF/MKhhwuwYbiuoVidFITsBrEstGBB4mzZA=", "email": "", "date_joined": "2012-08-02T08:30:11.562"}
        }
        hit = Hit(data)
        self.assertEquals('auth', hit.index)
        self.assertEquals('auth', hit._index)
        self.assertEquals('user', hit._type)
        self.assertEquals('user', hit.type)
        self.assertEquals('6', hit._id)
        self.assertEquals('6', hit.id)
        self.assertEquals('guillaume', hit.source.username)

class ResponseTest(TestCase):
    def setUp(self):
        # Setup a mock response
        ResponseMock._content = """{"took":2,"timed_out":false,"_shards":{"total":5,"successful":5,"failed":0},"hits":{"total":2,"max_score":1.0,"hits":[{"_index":"auth","_type":"user","_id":"6","_score":1.0, "_source" : {"username": "guillaume", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T08:30:11", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$M1nRKJfbvdQf$ouX5u9FOUF/MKhhwuwYbiuoVidFITsBrEstGBB4mzZA=", "email": "somemail@test.com", "date_joined": "2012-08-02T08:30:11"}},{"_index":"auth","_type":"user","_id":"8","_score":1.0, "_source" : {"username": "stephane", "first_name": "", "last_name": "", "is_active": true, "is_superuser": false, "is_staff": false, "last_login": "2012-08-02T09:14:38", "groups": [], "user_permissions": [], "password": "pbkdf2_sha256$10000$ORDHZAnNqTwF$UGmkUCyH0/uh1ruP93ZSTyog9Wi5g2qc+m/fxowigFs=", "email": "othermail@test.com", "date_joined": "2012-08-02T09:14:38"}}]}}"""
        from rubber import resource
        requestmock = RequestMock()
        resource.requests = requestmock

        from rubber import ElasticSearch
        self.client = ElasticSearch('foo', 'bar')


    def test_response_class(self):
        """
        Responses should be rubber.response.Response objects, except
        for the search response which should be a rubber.response.SearchResponse
        """

        response = self.client.search({})

        from rubber.response import Response, SearchResponse
        self.assertTrue(isinstance(response, Response))
        self.assertTrue(isinstance(response, SearchResponse))

        response = self.client.mapping.get()
        self.assertTrue(isinstance(response, Response))
        self.assertFalse(isinstance(response, SearchResponse))

    def test_response_json(self):
        """
        Responses should have a json property if json has been parsed.
        """
        response = self.client.search()
        self.assertTrue(isinstance(response.json, dict))


        # with invalid json
        ResponseMock._content = """;;;"""
        response = self.client.search()
        self.assertIsNone(response.json)
