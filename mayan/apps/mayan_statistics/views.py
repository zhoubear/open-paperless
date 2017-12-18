from __future__ import unicode_literals

from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from common.generics import ConfirmView, SimpleView, SingleObjectListView

from .classes import Statistic, StatisticNamespace
from .permissions import permission_statistics_view
from .tasks import task_execute_statistic


class NamespaceListView(SingleObjectListView):
    extra_context = {
        'hide_link': True,
        'title': _('Statistics namespaces'),
    }
    template_name = 'appearance/generic_list.html'
    view_permission = permission_statistics_view

    def get_object_list(self):
        return StatisticNamespace.get_all()


class NamespaceDetailView(SingleObjectListView):
    view_permission = permission_statistics_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'object': self.get_namespace(),
            'title': _('Namespace details for: %s') % self.get_namespace(),
        }

    def get_namespace(self):
        return StatisticNamespace.get(self.kwargs['slug'])

    def get_object_list(self):
        return self.get_namespace().statistics


class StatisticDetailView(SimpleView):
    view_permission = permission_statistics_view

    def get_extra_context(self):
        return {
            'chart_data': self.get_object().get_chart_data(),
            'namespace': self.get_object().namespace,
            'navigation_object_list': ('namespace', 'object'),
            'no_data': not self.get_object().get_results()['series'],
            'object': self.get_object(),
            'title': _('Results for: %s') % self.get_object(),
        }

    def get_object(self):
        try:
            return Statistic.get(self.kwargs['slug'])
        except KeyError:
            raise Http404(_('Statistic "%s" not found.') % self.kwargs['slug'])

    def get_template_names(self):
        return (self.get_object().renderer.template_name,)


class StatisticQueueView(ConfirmView):
    view_permission = permission_statistics_view

    def get_extra_context(self):
        return {
            'namespace': self.get_object().namespace,
            'object': self.get_object(),
            # Translators: This text is asking users if they want to queue
            # (to send to the queue) a statistic for it to be update ahead
            # of schedule
            'title': _(
                'Queue statistic "%s" to be updated?'
            ) % self.get_object(),
        }

    def get_object(self):
        try:
            return Statistic.get(self.kwargs['slug'])
        except KeyError:
            raise Http404(_('Statistic "%s" not found.') % self.kwargs['slug'])

    def get_post_action_redirect(self):
        return reverse(
            'statistics:namespace_details',
            args=(self.get_object().namespace.slug,)
        )

    def view_action(self):
        task_execute_statistic.delay(slug=self.get_object().slug)
