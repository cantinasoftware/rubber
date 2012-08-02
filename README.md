rubber
======

rubber is a Python client for Elasticsearch.

Its main features are:
  - rubber is easy to use
  - rubber integrates nicely with Django

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

    import rubber

    client = rubber.ElasticSearch('articles', 'article')

    # Searching
    for hit in client.search({'query':{'term':{'user':'kimshy'}}}).hits:
        print hit.source.user

    # Mapping
    client.mapping.put(my_mapping) # my_mapping is a dict object
    client.mapping.delete()
    mapping = client.mapping.get()

Django integration
------------------

    import rubber
    from django.db import models

    class Article(models.Model):
        elasticsearch = rubber.ElasticSearch()
        title = models.CharField(max_length=255)
        content = models.TextField()

    # Searching
    response = Article.elasticsearch.search(query) # query is a dict

    # Mapping
    Article.elasticsearch.mapping.put(mapping) # mapping is a dict

    # Auto save
    a = Article(title='I love ES')
    a.save()   # Automatically sent to elasticsearch
    a.delete() # Automatically removed from elasticsearch

Configuration
-------------

### Disabling the auto-save behavior for Django models

    import rubber
    from django.db import models

    class Article(models.Model):
        elasticsearch = rubber.ElasticSearch(auto_index=False)
        title = models.CharField(max_length=255)
        content = models.TextField()


### Configuring index name and document type for a Django model

    import rubber
    from django.db import models

    class Article(models.Model):
        elasticsearch = rubber.ElasticSearch(index_name='custom_index', type='custom_type')


### Saving to multiple indices

    import rubber
    from django.db import models

    class Article(models.Model):
        index1 = rubber.ElasticSearch(index_name='index1', type='type1')
        index2 = rubber.ElasticSearch(index_name='index2', type='type2')


