import os
from django import template

register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value.file.name)

# by mikeivanov (on April 16, 2007)


@register.filter
def in_list(value, arg):
    return value in arg
