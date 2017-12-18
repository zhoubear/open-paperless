from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from common.classes import DashboardWidget


def checkedout_documents_queryset():
    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )
    return DocumentCheckout.objects.all()


widget_checkouts = DashboardWidget(
    label=_('Checkedout documents'),
    link=reverse_lazy('checkouts:checkout_list'),
    icon='fa fa-shopping-cart', queryset=checkedout_documents_queryset
)
