from __future__ import absolute_import, unicode_literals

import logging

from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.views import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectEditView,
    SingleObjectListView
)

from .models import Transformation
from .permissions import (
    permission_transformation_create, permission_transformation_delete,
    permission_transformation_edit, permission_transformation_view
)

logger = logging.getLogger(__name__)


class TransformationDeleteView(SingleObjectDeleteView):
    model = Transformation

    def dispatch(self, request, *args, **kwargs):
        self.transformation = get_object_or_404(
            Transformation, pk=self.kwargs['pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_transformation_delete, user=request.user,
            obj=self.transformation.content_object
        )

        return super(TransformationDeleteView, self).dispatch(
            request, *args, **kwargs
        )

    def get_post_action_redirect(self):
        return reverse(
            'converter:transformation_list', args=(
                self.transformation.content_type.app_label,
                self.transformation.content_type.model,
                self.transformation.object_id
            )
        )

    def get_extra_context(self):
        return {
            'content_object': self.transformation.content_object,
            'navigation_object_list': ('content_object', 'transformation'),
            'previous': reverse(
                'converter:transformation_list', args=(
                    self.transformation.content_type.app_label,
                    self.transformation.content_type.model,
                    self.transformation.object_id
                )
            ),
            'title': _(
                'Delete transformation "%(transformation)s" for: '
                '%(content_object)s?'
            ) % {
                'transformation': self.transformation,
                'content_object': self.transformation.content_object
            },
            'transformation': self.transformation,
        }


class TransformationCreateView(SingleObjectCreateView):
    fields = ('name', 'arguments')

    def dispatch(self, request, *args, **kwargs):
        content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        try:
            self.content_object = content_type.get_object_for_this_type(
                pk=self.kwargs['object_id']
            )
        except content_type.model_class().DoesNotExist:
            raise Http404

        AccessControlList.objects.check_access(
            permissions=permission_transformation_create, user=request.user,
            obj=self.content_object
        )

        return super(TransformationCreateView, self).dispatch(
            request, *args, **kwargs
        )

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.content_object = self.content_object
        try:
            instance.full_clean()
            instance.save()
        except Exception as exception:
            logger.debug('Invalid form, exception: %s', exception)
            return super(TransformationCreateView, self).form_invalid(form)
        else:
            return super(TransformationCreateView, self).form_valid(form)

    def get_extra_context(self):
        return {
            'content_object': self.content_object,
            'navigation_object_list': ('content_object',),
            'title': _(
                'Create new transformation for: %s'
            ) % self.content_object,
        }

    def get_post_action_redirect(self):
        return reverse(
            'converter:transformation_list', args=(
                self.kwargs['app_label'], self.kwargs['model'],
                self.kwargs['object_id']
            )
        )

    def get_queryset(self):
        return Transformation.objects.get_for_model(self.content_object)


class TransformationEditView(SingleObjectEditView):
    fields = ('name', 'arguments', 'order')
    model = Transformation

    def dispatch(self, request, *args, **kwargs):
        self.transformation = get_object_or_404(
            Transformation, pk=self.kwargs['pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_transformation_edit, user=request.user,
            obj=self.transformation.content_object
        )

        return super(TransformationEditView, self).dispatch(
            request, *args, **kwargs
        )

    def form_valid(self, form):
        instance = form.save(commit=False)
        try:
            instance.full_clean()
            instance.save()
        except Exception as exception:
            logger.debug('Invalid form, exception: %s', exception)
            return super(TransformationEditView, self).form_invalid(form)
        else:
            return super(TransformationEditView, self).form_valid(form)

    def get_extra_context(self):
        return {
            'content_object': self.transformation.content_object,
            'navigation_object_list': ('content_object', 'transformation'),
            'title': _(
                'Edit transformation "%(transformation)s" for: %(content_object)s'
            ) % {
                'transformation': self.transformation,
                'content_object': self.transformation.content_object
            },
            'transformation': self.transformation,
        }

    def get_post_action_redirect(self):
        return reverse(
            'converter:transformation_list', args=(
                self.transformation.content_type.app_label,
                self.transformation.content_type.model,
                self.transformation.object_id
            )
        )


class TransformationListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        content_type = get_object_or_404(
            ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        try:
            self.content_object = content_type.get_object_for_this_type(
                pk=self.kwargs['object_id']
            )
        except content_type.model_class().DoesNotExist:
            raise Http404

        AccessControlList.objects.check_access(
            permissions=permission_transformation_view, user=request.user,
            obj=self.content_object
        )

        return super(TransformationListView, self).dispatch(
            request, *args, **kwargs
        )

    def get_extra_context(self):
        return {
            'content_object': self.content_object,
            'hide_link': True,
            'hide_object': True,
            'navigation_object_list': ('content_object',),
            'title': _('Transformations for: %s') % self.content_object,
        }

    def get_object_list(self):
        return Transformation.objects.get_for_model(self.content_object)
