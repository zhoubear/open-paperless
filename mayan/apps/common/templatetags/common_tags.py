from __future__ import unicode_literals

from json import dumps

import sh

from django.conf import settings
from django.template import Context, Library
from django.template.loader import get_template
from django.utils.encoding import force_text

import mayan

from ..classes import Collection, Dashboard
from ..utils import return_attrib

register = Library()

try:
    BUILD = sh.Command('git').bake('describe', '--tags', '--always', 'HEAD')
    DATE = sh.Command('git').bake('--no-pager', 'log', '-1', '--format=%cd')
except sh.CommandNotFound:
    BUILD = None
    DATE = None


@register.simple_tag
def get_collections():
    return Collection.get_all()


@register.simple_tag
def get_dashboard(name):
    return Dashboard.get(name=name)


@register.filter
def get_encoded_parameter(item, parameters_dict):
    result = {}
    for attrib_name, attrib in parameters_dict.items():
        result[attrib_name] = return_attrib(item, attrib)
    return dumps(result)


@register.filter
def object_property(value, arg):
    return return_attrib(value, arg)


@register.simple_tag
def project_copyright():
    return settings.PROJECT_COPYRIGHT


@register.simple_tag
def project_description():
    return getattr(settings, 'PROJECT_DESCRIPTION', mayan.__description__)


@register.simple_tag
def project_license():
    return settings.PROJECT_LICENSE


@register.simple_tag
def project_name():
    return settings.PROJECT_TITLE


@register.simple_tag
def project_website():
    return settings.PROJECT_WEBSITE


@register.simple_tag
def project_version():
    return mayan.__version__


@register.simple_tag(takes_context=True)
def render_subtemplate(context, template_name, template_context):
    """
    Renders the specified template with the mixed parent and
    subtemplate contexts
    """

    new_context = Context(context)
    new_context.update(Context(template_context))
    return get_template(template_name).render(new_context)


@register.simple_tag
def build():
    if BUILD:
        try:
            return '{} {}'.format(BUILD(), DATE())
        except sh.ErrorReturnCode_128:
            return ''
    else:
        return ''


@register.filter
def get_type(value):
    return force_text(type(value))
