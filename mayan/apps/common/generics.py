from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    FormView as DjangoFormView, DetailView, TemplateView
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import (
    CreateView, DeleteView, FormMixin, ModelFormMixin, UpdateView
)
from django.views.generic.list import ListView

from django_downloadview import (
    TextIteratorIO, VirtualDownloadView, VirtualFile
)
from pure_pagination.mixins import PaginationMixin

from .forms import ChoiceForm
from .mixins import (
    DeleteExtraDataMixin, DynamicFormViewMixin, ExtraContextMixin,
    FormExtraKwargsMixin, MultipleObjectMixin, ObjectActionMixin,
    ObjectListPermissionFilterMixin, ObjectNameMixin,
    ObjectPermissionCheckMixin, RedirectionMixin, ViewPermissionCheckMixin
)

from .settings import setting_paginate_by

__all__ = (
    'AssignRemoveView', 'ConfirmView', 'FormView', 'MultiFormView',
    'MultipleObjectConfirmActionView', 'MultipleObjectFormActionView',
    'SingleObjectCreateView', 'SingleObjectDeleteView',
    'SingleObjectDetailView', 'SingleObjectEditView', 'SingleObjectListView',
    'SimpleView'
)


class AssignRemoveView(ExtraContextMixin, ViewPermissionCheckMixin, ObjectPermissionCheckMixin, TemplateView):
    decode_content_type = False
    right_list_help_text = None
    left_list_help_text = None
    grouped = False
    left_list_title = None
    right_list_title = None
    template_name = 'appearance/generic_form.html'

    LEFT_LIST_NAME = 'left_list'
    RIGHT_LIST_NAME = 'right_list'

    @staticmethod
    def generate_choices(choices):
        results = []
        for choice in choices:
            ct = ContentType.objects.get_for_model(choice)
            label = force_text(choice)

            results.append(('%s,%s' % (ct.model, choice.pk), '%s' % (label)))

        # Sort results by the label not the key value
        return sorted(results, key=lambda x: x[1])

    def left_list(self):
        # Subclass must override
        raise NotImplementedError

    def right_list(self):
        # Subclass must override
        raise NotImplementedError

    def add(self, item):
        # Subclass must override
        raise NotImplementedError

    def remove(self, item):
        # Subclass must override
        raise NotImplementedError

    def get_disabled_choices(self):
        return ()

    def get_left_list_help_text(self):
        return self.left_list_help_text

    def get_right_list_help_text(self):
        return self.right_list_help_text

    def get(self, request, *args, **kwargs):
        self.unselected_list = ChoiceForm(
            prefix=self.LEFT_LIST_NAME, choices=self.left_list()
        )
        self.selected_list = ChoiceForm(
            prefix=self.RIGHT_LIST_NAME, choices=self.right_list(),
            disabled_choices=self.get_disabled_choices(),
            help_text=self.get_right_list_help_text()
        )
        return self.render_to_response(self.get_context_data())

    def process_form(self, prefix, items_function, action_function):
        if '%s-submit' % prefix in self.request.POST.keys():
            form = ChoiceForm(
                self.request.POST, prefix=prefix,
                choices=items_function()
            )

            if form.is_valid():
                for selection in form.cleaned_data['selection']:
                    if self.grouped:
                        flat_list = []
                        for group in items_function():
                            flat_list.extend(group[1])
                    else:
                        flat_list = items_function()

                    label = dict(flat_list)[selection]
                    if self.decode_content_type:
                        model, pk = selection.split(',')
                        selection_obj = ContentType.objects.get(
                            model=model
                        ).get_object_for_this_type(pk=pk)
                    else:
                        selection_obj = selection

                    try:
                        action_function(selection_obj)
                    except:
                        if settings.DEBUG:
                            raise
                        else:
                            messages.error(
                                self.request,
                                _('Unable to transfer selection: %s.') % label
                            )

    def post(self, request, *args, **kwargs):
        self.process_form(
            prefix=self.LEFT_LIST_NAME, items_function=self.left_list,
            action_function=self.add
        )
        self.process_form(
            prefix=self.RIGHT_LIST_NAME, items_function=self.right_list,
            action_function=self.remove
        )
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(AssignRemoveView, self).get_context_data(**kwargs)
        data.update({
            'subtemplates_list': [
                {
                    'name': 'appearance/generic_form_subtemplate.html',
                    'column_class': 'col-xs-12 col-sm-6 col-md-6 col-lg-6',
                    'context': {
                        'form': self.unselected_list,
                        'title': self.left_list_title or ' ',
                        'submit_label': _('Add'),
                        'submit_icon': 'fa fa-plus',
                        'hide_labels': True,
                    }
                },
                {
                    'name': 'appearance/generic_form_subtemplate.html',
                    'column_class': 'col-xs-12 col-sm-6 col-md-6 col-lg-6',
                    'context': {
                        'form': self.selected_list,
                        'title': self.right_list_title or ' ',
                        'submit_label': _('Remove'),
                        'submit_icon': 'fa fa-minus',
                        'hide_labels': True,
                    }
                },

            ],
        })
        return data


class ConfirmView(ObjectListPermissionFilterMixin, ObjectPermissionCheckMixin, ViewPermissionCheckMixin, ExtraContextMixin, RedirectionMixin, TemplateView):
    template_name = 'appearance/generic_confirm.html'

    def post(self, request, *args, **kwargs):
        self.view_action()
        return HttpResponseRedirect(self.get_success_url())


class FormView(ViewPermissionCheckMixin, ExtraContextMixin, RedirectionMixin, FormExtraKwargsMixin, DjangoFormView):
    template_name = 'appearance/generic_form.html'


class DynamicFormView(DynamicFormViewMixin, FormView):
    pass


class MultiFormView(DjangoFormView):
    prefix = None
    prefixes = {}

    def _create_form(self, form_name, klass):
        form_kwargs = self.get_form_kwargs(form_name)
        form_create_method = 'create_%s_form' % form_name
        if hasattr(self, form_create_method):
            form = getattr(self, form_create_method)(**form_kwargs)
        else:
            form = klass(**form_kwargs)
        return form

    def forms_valid(self, forms):
        for form_name, form in forms.items():
            form_valid_method = '%s_form_valid' % form_name

            if hasattr(self, form_valid_method):
                return getattr(self, form_valid_method)(form)

        self.all_forms_valid(forms)

        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))

    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        if 'forms' not in kwargs:
            kwargs['forms'] = self.get_forms(
                form_classes=self.get_form_classes()
            )
        return super(FormMixin, self).get_context_data(**kwargs)

    def get_form_classes(self):
        return self.form_classes

    def get_form_kwargs(self, form_name):
        kwargs = {}
        kwargs.update({'initial': self.get_initial(form_name)})
        kwargs.update({'prefix': self.get_prefix(form_name)})

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        return kwargs

    def get_forms(self, form_classes):
        return dict(
            [
                (
                    key, self._create_form(key, klass)
                ) for key, klass in form_classes.items()
            ]
        )

    def get_initial(self, form_name):
        initial_method = 'get_%s_initial' % form_name
        if hasattr(self, initial_method):
            return getattr(self, initial_method)()
        else:
            return self.initial.copy()

    def get_prefix(self, form_name):
        return self.prefixes.get(form_name, self.prefix)

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)

        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class MultipleObjectFormActionView(ObjectActionMixin, MultipleObjectMixin, FormExtraKwargsMixin, ViewPermissionCheckMixin, ExtraContextMixin, RedirectionMixin, DjangoFormView):
    """
    This view will present a form and upon receiving a POST request will
    perform an action on an object or queryset
    """
    template_name = 'appearance/generic_form.html'

    def __init__(self, *args, **kwargs):
        result = super(MultipleObjectFormActionView, self).__init__(*args, **kwargs)

        if self.__class__.mro()[0].get_queryset != MultipleObjectFormActionView.get_queryset:
            raise ImproperlyConfigured(
                '%(cls)s is overloading the get_queryset method. Subclasses '
                'should implement the get_object_list method instead. ' % {
                    'cls': self.__class__.__name__
                }
            )

        return result

    def form_valid(self, form):
        self.view_action(form=form)
        return super(MultipleObjectFormActionView, self).form_valid(form=form)

    def get_queryset(self):
        try:
            return super(MultipleObjectFormActionView, self).get_queryset()
        except ImproperlyConfigured:
            self.queryset = self.get_object_list()
            return super(MultipleObjectFormActionView, self).get_queryset()


class MultipleObjectConfirmActionView(ObjectActionMixin, MultipleObjectMixin, ObjectListPermissionFilterMixin, ViewPermissionCheckMixin, ExtraContextMixin, RedirectionMixin, TemplateView):
    template_name = 'appearance/generic_confirm.html'

    def post(self, request, *args, **kwargs):
        self.view_action()
        return HttpResponseRedirect(self.get_success_url())


class SimpleView(ViewPermissionCheckMixin, ExtraContextMixin, TemplateView):
    pass


class SingleObjectCreateView(ObjectNameMixin, ViewPermissionCheckMixin, ExtraContextMixin, RedirectionMixin, FormExtraKwargsMixin, CreateView):
    template_name = 'appearance/generic_form.html'

    def form_valid(self, form):
        # This overrides the original Django form_valid method

        self.object = form.save(commit=False)

        if hasattr(self, 'get_instance_extra_data'):
            for key, value in self.get_instance_extra_data().items():
                setattr(self.object, key, value)

        if hasattr(self, 'get_save_extra_data'):
            save_extra_data = self.get_save_extra_data()
        else:
            save_extra_data = {}

        try:
            self.object.save(**save_extra_data)
        except Exception as exception:
            context = self.get_context_data()

            messages.error(
                self.request,
                _('%(object)s not created, error: %(error)s') % {
                    'object': self.get_object_name(context=context),
                    'error': exception
                }
            )
        else:
            context = self.get_context_data()

            messages.success(
                self.request,
                _(
                    '%(object)s created successfully.'
                ) % {'object': self.get_object_name(context=context)}
            )

        return HttpResponseRedirect(self.get_success_url())


class SingleObjectDynamicFormCreateView(DynamicFormViewMixin, SingleObjectCreateView):
    pass


class SingleObjectDeleteView(ObjectNameMixin, DeleteExtraDataMixin, ViewPermissionCheckMixin, ObjectPermissionCheckMixin, ExtraContextMixin, RedirectionMixin, DeleteView):
    template_name = 'appearance/generic_confirm.html'

    def get_context_data(self, **kwargs):
        context = super(SingleObjectDeleteView, self).get_context_data(**kwargs)
        context.update({'delete_view': True})
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        object_name = self.get_object_name(context=context)

        try:
            result = super(SingleObjectDeleteView, self).delete(request, *args, **kwargs)
        except Exception as exception:
            messages.error(
                self.request,
                _('%(object)s not deleted, error: %(error)s.') % {
                    'object': object_name,
                    'error': exception
                }
            )

            raise exception
        else:
            messages.success(
                self.request,
                _(
                    '%(object)s deleted successfully.'
                ) % {'object': object_name}
            )

            return result


class SingleObjectDetailView(ViewPermissionCheckMixin, ObjectPermissionCheckMixin, FormExtraKwargsMixin, ExtraContextMixin, ModelFormMixin, DetailView):
    template_name = 'appearance/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super(SingleObjectDetailView, self).get_context_data(**kwargs)
        context.update({'read_only': True, 'form': self.get_form()})
        return context


class SingleObjectDownloadView(ViewPermissionCheckMixin, ObjectPermissionCheckMixin, VirtualDownloadView, SingleObjectMixin):
    TextIteratorIO = TextIteratorIO
    VirtualFile = VirtualFile


class SingleObjectEditView(ObjectNameMixin, ViewPermissionCheckMixin, ObjectPermissionCheckMixin, ExtraContextMixin, FormExtraKwargsMixin, RedirectionMixin, UpdateView):
    template_name = 'appearance/generic_form.html'

    def form_valid(self, form):
        # This overrides the original Django form_valid method

        self.object = form.save(commit=False)

        if hasattr(self, 'get_instance_extra_data'):
            for key, value in self.get_instance_extra_data().items():
                setattr(self.object, key, value)

        if hasattr(self, 'get_save_extra_data'):
            save_extra_data = self.get_save_extra_data()
        else:
            save_extra_data = {}

        context = self.get_context_data()
        object_name = self.get_object_name(context=context)

        try:
            self.object.save(**save_extra_data)
        except Exception as exception:
            messages.error(
                self.request,
                _('%(object)s not updated, error: %(error)s.') % {
                    'object': object_name,
                    'error': exception
                }
            )

            raise exception
        else:
            messages.success(
                self.request,
                _(
                    '%(object)s updated successfully.'
                ) % {'object': object_name}
            )

        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        obj = super(SingleObjectEditView, self).get_object(queryset=queryset)

        if hasattr(self, 'get_instance_extra_data'):
            for key, value in self.get_instance_extra_data().items():
                setattr(obj, key, value)

        return obj


class SingleObjectDynamicFormEditView(DynamicFormViewMixin, SingleObjectEditView):
    pass


class SingleObjectListView(PaginationMixin, ViewPermissionCheckMixin, ObjectListPermissionFilterMixin, ExtraContextMixin, RedirectionMixin, ListView):
    template_name = 'appearance/generic_list.html'

    def __init__(self, *args, **kwargs):
        result = super(SingleObjectListView, self).__init__(*args, **kwargs)

        if self.__class__.mro()[0].get_queryset != SingleObjectListView.get_queryset:
            raise ImproperlyConfigured(
                '%(cls)s is overloading the get_queryset method. Subclasses '
                'should implement the get_object_list method instead. ' % {
                    'cls': self.__class__.__name__
                }
            )

        return result

    def get_paginate_by(self, queryset):
        return setting_paginate_by.value

    def get_queryset(self):
        try:
            return super(SingleObjectListView, self).get_queryset()
        except ImproperlyConfigured:
            self.queryset = self.get_object_list()
            return super(SingleObjectListView, self).get_queryset()
