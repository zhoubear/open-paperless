from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.translation import ungettext, ugettext_lazy as _

from permissions import Permission

from acls.models import AccessControlList

from .forms import DynamicForm

__all__ = (
    'DeleteExtraDataMixin', 'DynamicFormViewMixin', 'ExtraContextMixin',
    'FormExtraKwargsMixin', 'MultipleObjectMixin', 'ObjectActionMixin',
    'ObjectListPermissionFilterMixin', 'ObjectNameMixin',
    'ObjectPermissionCheckMixin', 'RedirectionMixin',
    'ViewPermissionCheckMixin'
)


class DeleteExtraDataMixin(object):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if hasattr(self, 'get_delete_extra_data'):
            self.object.delete(**self.get_delete_extra_data())
        else:
            self.object.delete()

        return HttpResponseRedirect(success_url)


class DynamicFormViewMixin(object):
    form_class = DynamicForm

    def get_form_kwargs(self):
        data = super(DynamicFormViewMixin, self).get_form_kwargs()
        data.update({'schema': self.get_form_schema()})
        return data


class ExtraContextMixin(object):
    """
    Mixin that allows views to pass extra context to the template
    """

    extra_context = {}

    def get_extra_context(self):
        return self.extra_context

    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        context.update(self.get_extra_context())
        return context


class FormExtraKwargsMixin(object):
    """
    Mixin that allows a view to pass extra keyword arguments to forms
    """

    form_extra_kwargs = {}

    def get_form_extra_kwargs(self):
        return self.form_extra_kwargs

    def get_form_kwargs(self):
        result = super(FormExtraKwargsMixin, self).get_form_kwargs()
        result.update(self.get_form_extra_kwargs())
        return result


class MultipleInstanceActionMixin(object):
    # TODO: Deprecated, replace views using this with
    # MultipleObjectFormActionView or MultipleObjectConfirmActionView

    model = None
    success_message = _('Operation performed on %(count)d object')
    success_message_plural = _('Operation performed on %(count)d objects')

    def get_pk_list(self):
        return self.request.GET.get(
            'id_list', self.request.POST.get('id_list', '')
        ).split(',')

    def get_queryset(self):
        return self.model.objects.filter(pk__in=self.get_pk_list())

    def get_success_message(self, count):
        return ungettext(
            self.success_message,
            self.success_message_plural,
            count
        ) % {
            'count': count,
        }

    def post(self, request, *args, **kwargs):
        count = 0
        for instance in self.get_queryset():
            try:
                self.object_action(instance=instance)
            except PermissionDenied:
                pass
            else:
                count += 1

        messages.success(
            self.request,
            self.get_success_message(count=count)
        )

        return HttpResponseRedirect(self.get_success_url())


class MultipleObjectMixin(object):
    """
    Mixin that allows a view to work on a single or multiple objects
    """

    model = None
    object_permission = None
    pk_list_key = 'id_list'
    pk_list_separator = ','
    pk_url_kwarg = 'pk'
    queryset = None
    slug_url_kwarg = 'slug'

    def get_pk_list(self):
        result = self.request.GET.get(
            self.pk_list_key, self.request.POST.get(self.pk_list_key)
        )

        if result:
            return result.split(self.pk_list_separator)
        else:
            return None

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        pk_list = self.get_pk_list()

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        if pk_list is not None:
            queryset = queryset.filter(pk__in=self.get_pk_list())

        if pk is None and slug is None and pk_list is None:
            raise AttributeError(
                'Generic detail view %s must be called with '
                'either an object pk, a slug or an id list.'
                % self.__class__.__name__
            )

        if self.object_permission:
            return AccessControlList.objects.filter_by_access(
                self.object_permission, self.request.user, queryset=queryset
            )
        else:
            return queryset


class ObjectActionMixin(object):
    """
    Mixin that performs an user action to a queryset
    """

    success_message = 'Operation performed on %(count)d object'
    success_message_plural = 'Operation performed on %(count)d objects'

    def get_success_message(self, count):
        return ungettext(
            self.success_message,
            self.success_message_plural,
            count
        ) % {
            'count': count,
        }

    def object_action(self, instance, form=None):
        pass

    def view_action(self, form=None):
        self.action_count = 0

        for instance in self.get_queryset():
            try:
                self.object_action(form=form, instance=instance)
            except PermissionDenied:
                pass
            else:
                self.action_count += 1

        messages.success(
            self.request,
            self.get_success_message(count=self.action_count)
        )


class ObjectListPermissionFilterMixin(object):
    object_permission = None

    def get_queryset(self):
        queryset = super(ObjectListPermissionFilterMixin, self).get_queryset()

        if self.object_permission:
            return AccessControlList.objects.filter_by_access(
                self.object_permission, self.request.user, queryset=queryset
            )
        else:
            return queryset


class ObjectNameMixin(object):
    def get_object_name(self, context=None):
        if not context:
            context = self.get_context_data()

        object_name = context.get('object_name')

        if not object_name:
            try:
                object_name = self.object._meta.verbose_name
            except AttributeError:
                object_name = _('Object')

        return object_name


class ObjectPermissionCheckMixin(object):
    object_permission = None

    def get_permission_object(self):
        return self.get_object()

    def dispatch(self, request, *args, **kwargs):
        if self.object_permission:
            AccessControlList.objects.check_access(
                permissions=self.object_permission, user=request.user,
                obj=self.get_permission_object(),
                related=getattr(self, 'object_permission_related', None)
            )

        return super(
            ObjectPermissionCheckMixin, self
        ).dispatch(request, *args, **kwargs)


class RedirectionMixin(object):
    post_action_redirect = None
    action_cancel_redirect = None

    def dispatch(self, request, *args, **kwargs):
        post_action_redirect = self.get_post_action_redirect()
        action_cancel_redirect = self.get_action_cancel_redirect()

        self.next_url = self.request.POST.get(
            'next', self.request.GET.get(
                'next', post_action_redirect if post_action_redirect else self.request.META.get(
                    'HTTP_REFERER', resolve_url(settings.LOGIN_REDIRECT_URL)
                )
            )
        )
        self.previous_url = self.request.POST.get(
            'previous', self.request.GET.get(
                'previous', action_cancel_redirect if action_cancel_redirect else self.request.META.get(
                    'HTTP_REFERER', resolve_url(settings.LOGIN_REDIRECT_URL)
                )
            )
        )

        return super(
            RedirectionMixin, self
        ).dispatch(request, *args, **kwargs)

    def get_action_cancel_redirect(self):
        return self.action_cancel_redirect

    def get_context_data(self, **kwargs):
        context = super(RedirectionMixin, self).get_context_data(**kwargs)
        context.update(
            {
                'next': self.next_url,
                'previous': self.previous_url
            }
        )

        return context

    def get_post_action_redirect(self):
        return self.post_action_redirect

    def get_success_url(self):
        return self.next_url or self.previous_url


class ViewPermissionCheckMixin(object):
    view_permission = None

    def dispatch(self, request, *args, **kwargs):
        if self.view_permission:
            Permission.check_permissions(
                requester=self.request.user,
                permissions=(self.view_permission,)
            )

        return super(
            ViewPermissionCheckMixin, self
        ).dispatch(request, *args, **kwargs)
