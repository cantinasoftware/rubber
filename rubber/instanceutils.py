from requests.compat import json

def data_to_json(data):

    # convert dicts
    if isinstance(data, dict):
        return json.dumps(data)

    # convert objects that have a to_indexed_json method
    if 'to_indexed_json' in dir(data):
        return data.to_indexed_json()

    # convert django models
    try:
        from django.db import models
        if isinstance(data, models.Model):
            from django.core import serializers
            from django.core.serializers.json import DjangoJSONEncoder
            return json.dumps(serializers.serialize("python", [data])[0]['fields'], cls=DjangoJSONEncoder)
    except ImportError:
        pass

    return data

def get_pk(instance):
    if hasattr(instance, 'pk'):
        return instance.pk
    return None

