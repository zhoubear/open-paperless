from __future__ import unicode_literals

from django.apps import apps
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext


@python_2_unicode_compatible
class Collection(object):
    _registry = []

    @classmethod
    def get_all(cls):
        return sorted(cls._registry, key=lambda entry: entry._order)

    def __init__(self, label, icon=None, link=None, queryset=None, model=None, order=None):
        self._label = label
        self._icon = icon
        self._link = link
        self._queryset = queryset
        self._model = model
        self._order = order or 99
        self.__class__._registry.append(self)

    def __str__(self):
        return force_text(self.label)

    def resolve(self):
        self.children = self._get_children()
        self.icon = self._icon
        self.label = self._label
        self.url = None
        if self._link:
            self.icon = getattr(self._link, 'icon', self._icon)
            self.url = reverse(viewname=self._link.view, args=self._link.args)
        return ''

    def _get_children(self):
        if self._queryset:
            return self._queryset
        else:
            if self._model:
                return self._model.objects.all()


class Dashboard(object):
    _registry = {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, label):
        self.name = name
        self.label = label
        self.widgets = {}
        self.removed_widgets = []
        self.__class__._registry[name] = self

    def add_widget(self, widget, order=0):
        self.widgets[widget] = {'widget': widget, 'order': order}

    def get_widgets(self):
        """
        Returns a list of widgets sorted by their 'order'.
        If two or more widgets have the same 'order', sort by label.
        """
        return map(
            lambda x: x['widget'],
            filter(
                lambda x: x['widget'] not in self.removed_widgets,
                sorted(
                    self.widgets.values(),
                    key=lambda x: (x['order'], x['widget'].label)
                )
            )
        )

    def remove_widget(self, widget):
        self.removed_widgets.append(widget)


class DashboardWidget(object):
    _registry = []

    @classmethod
    def get_all(cls):
        return cls._registry

    def __init__(self, label, func=None, icon=None, link=None, queryset=None, statistic_slug=None):
        self.label = label
        self.icon = icon
        self.link = link
        self.queryset = queryset
        self.func = func
        self.statistic_slug = statistic_slug

        self.__class__._registry.append(self)


@python_2_unicode_compatible
class ErrorLogNamespace(object):
    def __init__(self, name, label=None):
        self.name = name
        self.label = label or name

    def __str__(self):
        return force_text(self.label)

    def create(self, obj, result):
        obj.error_logs.create(namespace=self.name, result=result)

    def all(self):
        ErrorLogEntry = apps.get_model(
            app_label='common', model_name='ErrorLogEntry'
        )

        return ErrorLogEntry.objects.filter(namespace=self.name)


@python_2_unicode_compatible
class Filter(object):
    _registry = {}

    @classmethod
    def get(cls, slug):
        return cls._registry[slug]

    @classmethod
    def all(cls):
        return cls._registry

    def __init__(self, label, slug, filter_kwargs, model, object_permission=None, hide_links=False):
        self.label = label
        self.slug = slug
        self.filter_kwargs = filter_kwargs
        self.model = model
        self.object_permission = object_permission
        self.hide_links = hide_links

        self.__class__._registry[self.slug] = self

    def __str__(self):
        return force_text(self.label)

    def get_queryset(self, user):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        queryset = self.model.objects.all()
        for kwargs in self.filter_kwargs:
            queryset = queryset.filter(**kwargs)

        queryset = queryset.distinct()

        if self.object_permission:
            return AccessControlList.objects.filter_by_access(
                self.object_permission, user, queryset=queryset
            )
        else:
            return queryset


class MissingItem(object):
    _registry = []

    @classmethod
    def get_all(cls):
        return cls._registry

    def __init__(self, label, condition, description, view):
        self.label = label
        self.condition = condition
        self.description = description
        self.view = view
        self.__class__._registry.append(self)


@python_2_unicode_compatible
class ModelAttribute(object):
    __registry = {}

    @classmethod
    def get_for(cls, model, type_names=None):
        result = []

        try:
            for type_name, attributes in cls.__registry[model].items():
                if not type_names or type_name in type_names:
                    result.extend(attributes)

            return result
        except IndexError:
            # We were passed a model instance, try again using the model of
            # the instance

            # If we are already in the model class, exit with an error
            if model.__class__ == models.base.ModelBase:
                raise

            return cls.get_for[type(model)]

    @classmethod
    def get_choices_for(cls, model, type_names=None):
        return [
            (
                attribute.name, attribute
            ) for attribute in cls.get_for(model, type_names)
        ]

    @classmethod
    def help_text_for(cls, model, type_names=None):
        result = []
        for count, attribute in enumerate(cls.get_for(model, type_names), 1):
            result.append(
                '{}) {}'.format(
                    count, force_text(attribute.get_display(show_name=True))
                )
            )

        return ' '.join(
            [ugettext('Available attributes: \n'), ', \n'.join(result)]
        )

    def get_display(self, show_name=False):
        if self.description:
            return '{} - {}'.format(
                self.name if show_name else self.label, self.description
            )
        else:
            return force_text(self.name if show_name else self.label)

    def __str__(self):
        return self.get_display()

    def __init__(self, model, name, label=None, description=None, type_name=None):
        self.model = model
        self.label = label
        self.name = name
        self.description = description

        for field in model._meta.fields:
            if field.name == name:
                self.label = field.verbose_name
                self.description = field.help_text

        self.__registry.setdefault(model, {})

        if isinstance(type_name, list):
            for single_type in type_name:
                self.__registry[model].setdefault(single_type, [])
                self.__registry[model][single_type].append(self)
        else:
            self.__registry[model].setdefault(type_name, [])
            self.__registry[model][type_name].append(self)


class Package(object):
    _registry = []

    @classmethod
    def get_all(cls):
        return cls._registry

    def __init__(self, label, license_text):
        self.label = label
        self.license_text = license_text
        self.__class__._registry.append(self)


class PropertyHelper(object):
    """
    Makes adding fields using __class__.add_to_class easier.
    Each subclass must implement the `constructor` and the `get_result`
    method.
    """
    @staticmethod
    @property
    def constructor(source_object):
        return PropertyHelper(source_object)

    def __init__(self, instance):
        self.instance = instance

    def __getattr__(self, name):
        return self.get_result(name=name)

    def get_result(self, name):
        """
        The method that produces the actual result. Must be implemented
        by each subclass.
        """
        raise NotImplementedError
