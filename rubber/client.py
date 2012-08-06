from rubber.resource import Resource
from rubber.response import Hit, Response
from rubber import settings

HANDLERS = {
    'search': '_search',
    'count': '_count',
    'mapping': '_mapping'
}

class ElasticSearch(object):
    def __init__(self, index_name=None, type=None, auto_index=True, hit_class=Hit, raise_on_error=False):
        self.index_name = index_name
        self.type = type
        self.auto_index = auto_index
        self.hit_class = hit_class
        self.raise_on_error = raise_on_error

    def contribute_to_class(self, model, name):
        if not self.index_name:
            self.index_name = model._meta.app_label

        if not self.type:
            self.type = model._meta.module_name

        self.model = model

        if self.auto_index and not getattr(settings, 'RUBBER_DISABLE_AUTO_INDEX', False):
            try:
                from django.db.models.signals import post_save, post_delete
                post_save.connect(self.django_post_save, sender=model)
                post_delete.connect(self.django_post_delete, sender=model)
            except ImportError, e:
                pass

        setattr(model, name, ElasticSearchDescriptor(self))

    def get(self, pk):
        return Resource(self.makepath(pk), wrapper=Response, raise_on_error=self.raise_on_error).get()

    def put(self, pk, instance):
        return Resource(self.makepath(pk), wrapper=Response, raise_on_error=self.raise_on_error).put(data=instance)

    def delete(self, pk):
        return Resource(self.makepath(pk), wrapper=Response, raise_on_error=self.raise_on_error).delete()

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
            if not name in HANDLERS.keys():
                raise e
            wrapper = Response
            if name == 'search': wrapper=self.wrapsearchresponse
            setattr(self, name, Resource(self.makepath(HANDLERS.get(name)), wrapper=wrapper, raise_on_error=self.raise_on_error))

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
            return InstanceResource(instance,
                                    self.elasticsearch.makepath(get_pk(instance)),
                                    wrapper=self.elasticsearch.wrapsearchresponse,
                                    raise_on_error=self.elasticsearch.raise_on_error)
        return self.elasticsearch
