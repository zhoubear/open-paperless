from __future__ import unicode_literals

from django.apps import apps
from django.utils.html import format_html_join

from .permissions import permission_cabinet_view


def jstree_data(node, selected_node):
    result = []
    result.append('{')
    result.append('"text": "{}",'.format(node.label))
    result.append(
        '"state": {{ "opened": true, "selected": {} }},'.format(
            'true' if node == selected_node else 'false'
        )
    )
    result.append(
        '"data": {{ "href": "{}" }},'.format(node.get_absolute_url())
    )

    children = node.get_children().order_by('label',)

    if children:
        result.append('"children" : [')
        for child in children:
            result.extend(jstree_data(node=child, selected_node=selected_node))

        result.append(']')

    result.append('},')

    return result


def widget_document_cabinets(document, user):
    """
    A cabinet widget that displays the cabinets for the given document
    """
    AccessControlList = apps.get_model(
        app_label='acls', model_name='AccessControlList'
    )

    cabinets = AccessControlList.objects.filter_by_access(
        permission_cabinet_view, user, queryset=document.document_cabinets().all()
    )

    return format_html_join(
        '\n', '<div class="cabinet-display">{}</div>',
        (
            (cabinet.get_full_path(),) for cabinet in cabinets
        )
    )
