rubber
======

rubber is a Python client for Elasticsearch.

Its main features are:
  - rubber is easy to use
  - rubber does not try to hide or wrap Elasticsearch syntax.
  - rubber integrates nicely with Django:
    - automatically saves your models to Elasticsearch
    - provides a Manager-style object on your django models
      for querying
  - rubber is unit-testing friendly: you don't need an
    elasticsearch instance to run your tests

Dependencies
============

rubber needs the 'requests' Python package.

Installation
============

    pip install rubber

Usage
=====

Basic usage
----------

### Creating an ElasticSearch client

The main class is rubber.ElasticSearch.
You instanciate a rubber.ElasticSearch object for an index_name and a document type, like this:

    import rubber

    client = rubber.ElasticSearch('articles', 'article')

    # -OR-

    client = rubber.ElasticSearch('articles')

### The client interface

Once you have such an object, you can GET/PUT/POST/DELETE on the __search_, _count_ and __mapping_ endpoints.
These endpoints are available on the _search_, _count_ and _mapping_ properties of the client:

    client.search
    client.mapping
    client.count

You can GET/PUT/POST/DELETE on each endpoint like this:

    response = client.mapping.get()
    response = client.mapping.put(somedict)
    response = client.mapping.delete()

All four methods (get/put/post/delete) are directly mapped on [their equivalent _requests_ method](http://docs.python-requests.org/en/latest/api/#requests.Request),
this means that you can pass any additional parameter that the requests library accepts (files, headers, cookies, etc.).

    response = client.search.get(params={"q":"*"})

Each endpoint is callable and defaults to get(). That means that you can search like this:

    response = client.search() # Equivalent to client.search.get()

### Response objects

Responses are just like request.models.Response objects returned by the _requests_ library we use under the hood.
You can get the corresponding JSON like this:

    somedict = response.json

More information is also avalable (see the [requests documentation](http://docs.python-requests.org/en/latest/api/#requests.Response)):

    headers = response.headers
    status = response.status_code

If you were searching, you can additionnaly look that _response.results_,
to get a HitCollection, which is an iterable over Hit objects.

    results = response.results
    for hit in results:
        print "%s: %s" % (hit.source.title, hit.score)

### Hit objects

Hit objects are plain Python objects, they give you object notation over the resulting JSON.
As a convenience, they also allow you to get '_' properties without the uderscore, like this:

    hit.source    # => the '_source' property of the JSON hit
    hit._source   # => the exact same thing
    hit.score     # => the '_score'

### Advanced configuration

#### HTTP configuration

Since rubber is based on the [requests library](http://python-requests.org), 
you can configure every aspect of the HTTP request/response cycle directly
through [_requests_ configuration options](http://docs.python-requests.org/en/latest/user/advanced/#configuring-requests).

#### Error behavior

By default, any error calling elasticsearch will yield a None response and log the exception.
This can be changed when instanciating a rubber.ElasticSearch:

    es = rubber.ElasticSearch(raise_on_error=True)

### Unit testing

You probably want to be able to run unit tests without having Elasticsearch running.
If that is the case, rubber has a configuration option that allows you to mock
content returned by elasticsearch.

Just set rubber.settings.RUBBER_MOCK_HTTP_RESPONSE to a string that should be the response body
and you're set.

Django integration
------------------

### Integrating rubber into your models

Rubber lets you add an 'elasticsearch' property on your models, like this:

    import rubber
    from django.db import models

    class Article(models.Model):
        # Elasticsearch
        elasticsearch = rubber.ElasticSearch()

        title = models.CharField(max_length=255)
        content = models.TextField()

### Saving your models to Elasticsearch

By default, adding a rubber.ElasticSearch instance to your model
will automatically save it to Elasticsearch.

This can be turned off:

    class Article(models.Model):
        # Elasticsearch
        elasticsearch = rubber.ElasticSearch(auto_index=False)

### Controlling the index name and document type

By default rubber will store all the models of the same Django app in the same index,
with a different document type for each model.

The index name is the name of the app. The document type is the name of the model ('article' in our example)

This can be changed like this:

    class Article(models.Model):
        # Elasticsearch
        elasticsearch = rubber.ElasticSearch(index_name='someindex', type='somedocumenttype')

### Storing a model in multiple indices

You can add as many rubber.ElasticSearch properties to your model, each one saving to a different index / document type,
like this:

    class Article(models.Model):
        index1 = rubber.ElasticSearch(index_name='index1', type='type1')
        index2 = rubber.ElasticSearch(index_name='index2', type='type2')

### Searching your models

You can use the 'elasticsearch' instance on your model class like this:

    # Searching
    response = Article.elasticsearch.search(query) # query is a dict

    # Mapping
    response = Article.elasticsearch.mapping.put(mapping) # mapping is a dict

### Manually indexing your models

The 'elasticsearch' property will be propagated to your model instances, bound to the specific instance
you are working with:

    article = Article.objects.get(pk=1)

    response = article.elasticsearch.put() # Index this document
    response = article.elasticsearch.delete() # Delete this document

Other clients
=============

Check out [other elasticsearch clients](http://www.elasticsearch.org/guide/appendix/clients.html)

