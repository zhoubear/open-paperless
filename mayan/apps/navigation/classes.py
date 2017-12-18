from __future__ import unicode_literals

import inspect
import logging

from furl import furl

from django.apps import apps
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
from django.template import VariableDoesNotExist, Variable
from django.template.defaulttags import URLNode
from django.urls import resolve
from django.utils.encoding import force_str, force_text

from common.utils import return_attrib
from permissions import Permission

logger = logging.getLogger(__name__)


class ResolvedLink(object):
    def __init__(self, link, current_view):
        self.current_view = current_view
        self.disabled = False
        self.link = link
        self.url = '#'
        self.context = None
        self.request = None

    @property
    def active(self):
        return self.link.view == self.current_view

    @property
    def description(self):
        return self.link.description

    @property
    def icon(self):
        return self.link.icon

    @property
    def tags(self):
        return self.link.tags

    @property
    def text(self):
        try:
            return self.link.text(context=self.context)
        except TypeError:
            return self.link.text


class Menu(object):
    _registry = {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def remove(cls, name):
        del cls._registry[name]

    def __init__(self, name, icon=None, label=None):
        if name in self.__class__._registry:
            raise Exception('A menu with this name already exists')

        self.icon = icon
        self.name = name
        self.label = label
        self.bound_links = {}
        self.unbound_links = {}
        self.link_positions = {}
        self.__class__._registry[name] = self

    def _map_links_to_source(self, links, source, map_variable='bound_links', position=None):
        source_links = getattr(self, map_variable).setdefault(source, [])

        for link in links:
            source_links.append(link)
            self.link_positions[link] = position

    def bind_links(self, links, sources=None, position=None):
        """
        Associate a link to a model, a view inside this menu
        """

        try:
            for source in sources:
                self._map_links_to_source(
                    links=links, position=position, source=source
                )
        except TypeError:
            # Unsourced links display always
            self._map_links_to_source(
                links=links, position=position, source=sources
            )

    def get_resolved_navigation_object_list(self, context, source):
        resolved_navigation_object_list = []

        if source:
            resolved_navigation_object_list = [source]
        else:
            navigation_object_list = context.get(
                'navigation_object_list', ('object',)
            )

            logger.debug('navigation_object_list: %s', navigation_object_list)

            # Multiple objects
            for navigation_object in navigation_object_list:
                try:
                    resolved_navigation_object_list.append(
                        Variable(navigation_object).resolve(context)
                    )
                except VariableDoesNotExist:
                    pass

        logger.debug(
            'resolved_navigation_object_list: %s',
            force_text(resolved_navigation_object_list)
        )
        return resolved_navigation_object_list

    def resolve(self, context, source=None):
        result = []

        try:
            request = Variable('request').resolve(context)
        except VariableDoesNotExist:
            # There is no request variable, most probable a 500 in a test view
            # Don't return any resolved links then.
            logger.warning('No request variable, aborting menu resolution')
            return ()

        current_path = request.META['PATH_INFO']

        # Get sources: view name, view objects
        current_view = resolve(current_path).view_name

        resolved_navigation_object_list = self.get_resolved_navigation_object_list(
            context=context, source=source
        )

        for resolved_navigation_object in resolved_navigation_object_list:
            resolved_links = []

            for bound_source, links in self.bound_links.items():
                try:
                    if inspect.isclass(bound_source):
                        if type(resolved_navigation_object) == bound_source:
                            for link in links:
                                resolved_link = link.resolve(
                                    context=context,
                                    resolved_object=resolved_navigation_object
                                )
                                if resolved_link:
                                    if resolved_link.link not in self.unbound_links.get(bound_source, ()):
                                        resolved_links.append(resolved_link)
                            # No need for further content object match testing
                            break
                        elif hasattr(resolved_navigation_object, 'get_deferred_fields') and resolved_navigation_object.get_deferred_fields() and isinstance(resolved_navigation_object, bound_source):
                            # Second try for objects using .defer() or .only()
                            for link in links:
                                resolved_link = link.resolve(
                                    context=context,
                                    resolved_object=resolved_navigation_object
                                )
                                if resolved_link:
                                    if resolved_link.link not in self.unbound_links.get(bound_source, ()):
                                        resolved_links.append(resolved_link)
                            # No need for further content object match testing
                            break
                except TypeError:
                    # When source is a dictionary
                    pass

            if resolved_links:
                result.append(resolved_links)

        resolved_links = []
        # View links
        for link in self.bound_links.get(current_view, []):
            resolved_link = link.resolve(context=context)
            if resolved_link:
                if resolved_link.link not in self.unbound_links.get(current_view, ()):
                    resolved_links.append(resolved_link)

        if resolved_links:
            result.append(resolved_links)

        resolved_links = []

        # Main menu links
        for link in self.bound_links.get(None, []):
            if isinstance(link, Menu):
                resolved_link = link
                if resolved_link not in self.unbound_links.get(None, ()):
                    resolved_links.append(resolved_link)
            else:
                # "Always show" links
                resolved_link = link.resolve(context=context)
                if resolved_link:
                    if resolved_link.link not in self.unbound_links.get(None, ()):
                        resolved_links.append(resolved_link)

        if resolved_links:
            result.append(resolved_links)

        if result:
            # Sort links by position value passed during bind
            result[0] = sorted(
                result[0], key=lambda item: (self.link_positions.get(item.link) or 0) if isinstance(item, ResolvedLink) else (self.link_positions.get(item) or 0)
            )

        return result

    def unbind_links(self, links, sources=None):
        """
        Allow unbinding links from sources, used to allow 3rd party apps to
        change the link binding of core apps
        """

        try:
            for source in sources:
                self._map_links_to_source(
                    links=links, source=source, map_variable='unbound_links'
                )
        except TypeError:
            # Unsourced links display always
            self._map_links_to_source(
                links=links, source=sources, map_variable='unbound_links'
            )


class Link(object):
    def __init__(self, text, view=None, args=None, condition=None,
                 conditional_disable=None, description=None, icon=None,
                 keep_query=False, kwargs=None, permissions=None,
                 permissions_related=None, remove_from_query=None, tags=None,
                 url=None):

        self.args = args or []
        self.condition = condition
        self.conditional_disable = conditional_disable
        self.description = description
        self.icon = icon
        self.keep_query = keep_query
        self.kwargs = kwargs or {}
        self.permissions = permissions or []
        self.permissions_related = permissions_related
        self.remove_from_query = remove_from_query or []
        self.tags = tags
        self.text = text
        self.view = view
        self.url = url

    def resolve(self, context, resolved_object=None):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        request = Variable('request').resolve(context)
        current_path = request.META['PATH_INFO']
        current_view = resolve(current_path).view_name

        # ACL is tested agains the resolved_object or just {{ object }} if not
        if not resolved_object:
            try:
                resolved_object = Variable('object').resolve(context=context)
            except VariableDoesNotExist:
                pass

        # If this link has a required permission check that the user has it
        # too
        if self.permissions:
            if resolved_object:
                try:
                    AccessControlList.objects.check_access(
                        permissions=self.permissions, user=request.user,
                        obj=resolved_object, related=self.permissions_related
                    )
                except PermissionDenied:
                    return None
            else:
                try:
                    Permission.check_permissions(
                        requester=request.user, permissions=self.permissions
                    )
                except PermissionDenied:
                    return None

        # Check to see if link has conditional display function and only
        # display it if the result of the conditional display function is
        # True
        if self.condition:
            if not self.condition(context):
                return None

        resolved_link = ResolvedLink(current_view=current_view, link=self)

        if self.view:
            view_name = Variable('"{}"'.format(self.view))
            if isinstance(self.args, list) or isinstance(self.args, tuple):
                # TODO: Don't check for instance check for iterable in try/except
                # block. This update required changing all 'args' argument in
                # links.py files to be iterables and not just strings.
                args = [Variable(arg) for arg in self.args]
            else:
                args = [Variable(self.args)]

            # If we were passed an instance of the view context object we are
            # resolving, inject it into the context. This help resolve links for
            # object lists.
            if resolved_object:
                context['resolved_object'] = resolved_object

            try:
                kwargs = self.kwargs(context)
            except TypeError:
                # Is not a callable
                kwargs = self.kwargs

            kwargs = {key: Variable(value) for key, value in kwargs.items()}

            # Use Django's exact {% url %} code to resolve the link
            node = URLNode(
                view_name=view_name, args=args, kwargs=kwargs, asvar=None
            )
            try:
                resolved_link.url = node.render(context)
            except Exception as exception:
                logger.error(
                    'Error resolving link "%s" URL; %s', self.text, exception
                )
        elif self.url:
            resolved_link.url = self.url

        # This is for links that should be displayed but that are not clickable
        if self.conditional_disable:
            resolved_link.disabled = self.conditional_disable(context)
        else:
            resolved_link.disabled = False

        # Lets a new link keep the same URL query string of the current URL
        if self.keep_query:
            # Sometimes we are required to remove a key from the URL QS
            parsed_url = furl(
                force_str(
                    request.get_full_path() or request.META.get(
                        'HTTP_REFERER', resolve_url(settings.LOGIN_REDIRECT_URL)
                    )
                )
            )

            for key in self.remove_from_query:
                try:
                    parsed_url.query.remove(key)
                except KeyError:
                    pass

            # Use the link's URL but with the previous URL querystring
            new_url = furl(resolved_link.url)
            new_url.args = parsed_url.querystr
            resolved_link.url = new_url.url

        resolved_link.context = context
        return resolved_link


class Separator(Link):
    """
    Menu separator. Renders to an <hr> tag
    """
    def __init__(self, *args, **kwargs):
        self.icon = None
        self.text = None
        self.view = None

    def resolve(self, *args, **kwargs):
        result = ResolvedLink(current_view=None, link=self)
        result.separator = True
        return result


class SourceColumn(object):
    _registry = {}

    @staticmethod
    def sort(columns):
        return sorted(columns, key=lambda x: x.order)

    @classmethod
    def get_for_source(cls, source):
        try:
            return SourceColumn.sort(columns=cls._registry[source])
        except KeyError:
            try:
                # Try it as a queryset
                return SourceColumn.sort(columns=cls._registry[source.model])
            except AttributeError:
                try:
                    # It seems to be an instance, try its class
                    return SourceColumn.sort(columns=cls._registry[source.__class__])
                except KeyError:
                    try:
                        # Special case for queryset items produced from
                        # .defer() or .only() optimizations
                        return SourceColumn.sort(columns=cls._registry[source._meta.parents.items()[0][0]])
                    except (AttributeError, KeyError, IndexError):
                        return ()
        except TypeError:
            # unhashable type: list
            return ()

    def __init__(self, source, label, attribute=None, func=None, order=None):
        self.source = source
        self.label = label
        self.attribute = attribute
        self.func = func
        self.order = order or 0
        self.__class__._registry.setdefault(source, [])
        self.__class__._registry[source].append(self)

    def resolve(self, context):
        if self.attribute:
            result = return_attrib(context['object'], self.attribute)
        elif self.func:
            result = self.func(context=context)

        return result


class Text(Link):
    """
    Menu text. Renders to a plain <li> tag
    """
    def __init__(self, *args, **kwargs):
        self.icon = None
        self.text = kwargs.get('text')
        self.view = None

    def resolve(self, *args, **kwargs):
        result = ResolvedLink(current_view=None, link=self)
        result.context = kwargs.get('context')
        result.text_span = True
        return result
