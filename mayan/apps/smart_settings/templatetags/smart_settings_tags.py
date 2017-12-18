from __future__ import unicode_literals

from django.template import Library

from ..classes import Setting

register = Library()


@register.simple_tag
def smart_setting(global_name):
    return Setting.get(global_name=global_name)
