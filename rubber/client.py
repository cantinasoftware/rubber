from rubber.resource import Resource
from rubber.response import Hit, Response

class ElasticSearch(object):
    def __init__(self, index_name=None, type=None, auto_index=True, hit_class=Hit):
        self.index_name = index_name
        self.type = type
        self.auto_index = auto_index
        self.hit_class = hit_class

    def contribute_to_class(self, model, name):
        if not self.index_name:
            self.index_name = model._meta.app_label

        if not self.type:
            self.type = model._meta.module_name

        self.model = model

        if self.auto_index:
            try:
                from django.db.models.signals import post_save, post_delete
                post_save.connect(self.django_post_save, sender=model)
                post_delete.connect(self.django_post_delete, sender=model)
            except ImportError, e:
                pass

        setattr(model, name, ElasticSearchDescriptor(self))

    def get(self, pk):
        return Resource(self.makepath(pk), wrapper=Response).get()

    def put(self, pk, instance):
        return Resource(self.makepath(pk), wrapper=Response).put(data=instance)

    def delete(self, pk):
        return Resource(self.makepath(pk), wrapper=Response).delete()

    def django_post_delete(self, sender, instance, **kwargs):
        from rubber.instanceutils import get_pk
        self.delete(get_pk(instance))

    def django_post_save(self, sender, instance, created, **kwargs):
        from rubber.instanceutils import get_pk
        self.put(get_pk(instance), instance)

    def __getattribute__(self, name):
        default_impl = super(ElasticSearch, self).__getattribute__
        try:
            return default_impl(name)
        except AttributeError, e:
            if not name in ('search', 'mapping'):
                raise e
            if name == 'search':
                setattr(self, name, Resource(self.makepath("_%s"%name), wrapper=self.wrapsearchresponse))
            else:
                setattr(self, name, Resource(self.makepath("_%s"%name), wrapper=Response))

            return default_impl(name)

    def makepath(self, name):
        tokens = []
        if self.index_name:
            tokens.append(str(self.index_name))
        if self.type:
            tokens.append(str(self.type))
        if name:
            tokens.append(str(name))
        return "/".join(tokens)

    def wrapsearchresponse(self, resp):
        from rubber.response import SearchResponse
        return SearchResponse(resp, hit_class=self.hit_class)

class ElasticSearchDescriptor(object):

    def __init__(self, elasticsearch):
        self.elasticsearch = elasticsearch

    def __get__(self, instance, type=None):
        if instance != None:
            from rubber.resource import InstanceResource
            from rubber.instanceutils import get_pk
            return InstanceResource(instance, self.elasticsearch.makepath(get_pk(instance)), wrapper=self.elasticsearch.wrapsearchresponse)
        return self.elasticsearch
