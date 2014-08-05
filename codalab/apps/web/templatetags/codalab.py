import os
from django import template
from django.contrib.contenttypes.models import ContentType


register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value.file.name)

# by mikeivanov (on April 16, 2007)


@register.filter
def in_list(value, arg):
    return value in arg

@register.filter
def get_type(value):
    if hasattr(value, '_type'):
        if value._type is not None:
            value._type = ContentType.objects.get_for_model(value)
    else:
        value._type = value.__class__.__name__
    return value._type

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_by_name(dictionary, key):
    return filter(lambda x: x['name'] == key, dictionary)

@register.filter
def get_array_or_attr(elem, attribute):
    if attribute in elem and len(elem[attribute]) > 0:
        return elem[attribute]
    else:
        return [elem]
