from __future__ import absolute_import, unicode_literals

from json import dumps

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, resolve_url
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils import timezone, translation
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.generic import RedirectView, TemplateView

from acls.models import AccessControlList

from .classes import Filter
from .exceptions import NotLatestVersion
from .forms import (
    FilterForm, LicenseForm, LocaleProfileForm, LocaleProfileForm_view,
    PackagesLicensesForm, UserForm, UserForm_view
)
from .generics import (  # NOQA
    AssignRemoveView, ConfirmView, FormView, MultiFormView,
    MultipleObjectConfirmActionView, MultipleObjectFormActionView,
    SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectDetailView, SingleObjectDynamicFormCreateView,
    SingleObjectDynamicFormEditView, SingleObjectDownloadView,
    SingleObjectEditView, SingleObjectListView, SimpleView
)
from .menus import menu_tools, menu_setup
from .permissions_runtime import permission_error_log_view
from .utils import check_version


class AboutView(TemplateView):
    template_name = 'appearance/about.html'


class CheckVersionView(SimpleView):
    template_name = 'appearance/generic_template.html'

    def get_extra_context(self):
        try:
            check_version()
        except NotLatestVersion as exception:
            message = _(
                'The version you are using is outdated. The latest version '
                'is %s'
            ) % exception.upstream_version
        else:
            message = _('Your version is up-to-date.')

        return {
            'title': _('Check for updates'),
            'content': message
        }


class CurrentUserDetailsView(SingleObjectDetailView):
    form_class = UserForm_view

    def get_object(self):
        return self.request.user

    def get_extra_context(self, **kwargs):
        return {
            'object': None,
            'title': _('Current user details'),
        }


class CurrentUserEditView(SingleObjectEditView):
    extra_context = {'object': None, 'title': _('Edit current user details')}
    form_class = UserForm
    post_action_redirect = reverse_lazy('common:current_user_details')

    def get_object(self):
        return self.request.user


class CurrentUserLocaleProfileDetailsView(TemplateView):
    template_name = 'appearance/generic_form.html'

    def get_context_data(self, **kwargs):
        data = super(
            CurrentUserLocaleProfileDetailsView, self
        ).get_context_data(**kwargs)
        data.update({
            'form': LocaleProfileForm_view(
                instance=self.request.user.locale_profile
            ),
            'read_only': True,
            'title': _('Current user locale profile details'),
        })
        return data


class CurrentUserLocaleProfileEditView(SingleObjectEditView):
    extra_context = {
        'title': _('Edit current user locale profile details')
    }
    form_class = LocaleProfileForm
    post_action_redirect = reverse_lazy(
        'common:current_user_locale_profile_details'
    )

    def form_valid(self, form):
        form.save()

        timezone.activate(form.cleaned_data['timezone'])
        translation.activate(form.cleaned_data['language'])

        if hasattr(self.request, 'session'):
            self.request.session[
                translation.LANGUAGE_SESSION_KEY
            ] = form.cleaned_data['language']
            self.request.session[
                settings.TIMEZONE_SESSION_KEY
            ] = form.cleaned_data['timezone']
        else:
            self.request.set_cookie(
                settings.LANGUAGE_COOKIE_NAME, form.cleaned_data['language']
            )
            self.request.set_cookie(
                settings.TIMEZONE_COOKIE_NAME, form.cleaned_data['timezone']
            )

        return super(CurrentUserLocaleProfileEditView, self).form_valid(form)

    def get_object(self):
        return self.request.user.locale_profile


class FaviconRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        """
        Hide the static tag import to avoid errors with static file
        processors
        """
        from django.contrib.staticfiles.templatetags.staticfiles import static
        return static('appearance/images/favicon.ico')


class FilterSelectView(SimpleView):
    form_class = FilterForm
    template_name = 'appearance/generic_form.html'

    def get_form(self):
        return FilterForm()

    def get_extra_context(self):
        return {
            'form': self.get_form(),
            'title': _('Filter selection')
        }

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(
            reverse(
                'common:filter_results',
                args=(request.POST.get('filter_slug'),)
            )
        )


class FilterResultListView(SingleObjectListView):
    def get_extra_context(self):
        return {
            'hide_links': self.get_filter().hide_links,
            'title': _('Results for filter: %s') % self.get_filter()
        }

    def get_filter(self):
        try:
            return Filter.get(self.kwargs['slug'])
        except KeyError:
            raise Http404(ugettext('Filter not found'))

    def get_object_list(self):
        return self.get_filter().get_queryset(user=self.request.user)


class HomeView(TemplateView):
    template_name = 'appearance/home.html'


class LicenseView(SimpleView):
    extra_context = {
        'form': LicenseForm(),
        'read_only': True,
        'title': _('License'),
    }
    template_name = 'appearance/generic_form.html'


class ObjectErrorLogEntryListClearView(ConfirmView):
    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Clear error log entries for: %s' % self.get_object()),
        }

    def get_object(self):
        content_type = get_object_or_404(
            klass=ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        return get_object_or_404(
            klass=content_type.model_class(),
            pk=self.kwargs['object_id']
        )

    def view_action(self):
        self.get_object().error_logs.all().delete()
        messages.success(
            self.request, _('Object error log cleared successfully')
        )


class ObjectErrorLogEntryListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            obj=self.get_object(), permissions=permission_error_log_view,
            user=request.user
        )

        return super(ObjectErrorLogEntryListView, self).dispatch(
            request, *args, **kwargs
        )

    def get_extra_context(self):
        return {
            'extra_columns': (
                {'name': _('Date and time'), 'attribute': 'datetime'},
                {'name': _('Result'), 'attribute': 'result'},
            ),
            'hide_object': True,
            'object': self.get_object(),
            'title': _('Error log entries for: %s' % self.get_object()),
        }

    def get_object(self):
        content_type = get_object_or_404(
            klass=ContentType, app_label=self.kwargs['app_label'],
            model=self.kwargs['model']
        )

        return get_object_or_404(
            klass=content_type.model_class(), pk=self.kwargs['object_id']
        )

    def get_object_list(self):
        return self.get_object().error_logs.all()


class PackagesLicensesView(SimpleView):
    template_name = 'appearance/generic_form.html'

    def get_extra_context(self):
        # Use a function so that PackagesLicensesForm get initialized at every
        # request
        return {
            'form': PackagesLicensesForm(),
            'read_only': True,
            'title': _('Other packages licenses'),
        }


class SetupListView(TemplateView):
    template_name = 'appearance/generic_list_horizontal.html'

    def get_context_data(self, **kwargs):
        data = super(SetupListView, self).get_context_data(**kwargs)
        context = RequestContext(self.request)
        context['request'] = self.request
        data.update({
            'resolved_links': menu_setup.resolve(context=context),
            'title': _('Setup items'),
        })
        return data


class ToolsListView(SimpleView):
    template_name = 'appearance/generic_list_horizontal.html'

    def get_menu_links(self):
        context = RequestContext(self.request)
        context['request'] = self.request

        return menu_tools.resolve(context=context)

    def get_extra_context(self):
        return {
            'resolved_links': self.get_menu_links(),
            'title': _('Tools'),
        }


def multi_object_action_view(request):
    """
    Proxy view called first when using a multi object action, which
    then redirects to the appropiate specialized view
    """

    next = request.POST.get(
        'next', request.GET.get(
            'next', request.META.get(
                'HTTP_REFERER', resolve_url(settings.LOGIN_REDIRECT_URL)
            )
        )
    )

    action = request.GET.get('action', None)
    id_list = ','.join(
        [key[3:] for key in request.GET.keys() if key.startswith('pk_')]
    )
    items_property_list = [
        (key[11:]) for key in request.GET.keys() if key.startswith('properties_')
    ]

    if not action:
        messages.error(request, _('No action selected.'))
        return HttpResponseRedirect(
            request.META.get(
                'HTTP_REFERER', resolve_url(settings.LOGIN_REDIRECT_URL)
            )
        )

    if not id_list and not items_property_list:
        messages.error(request, _('Must select at least one item.'))
        return HttpResponseRedirect(
            request.META.get(
                'HTTP_REFERER', resolve_url(settings.LOGIN_REDIRECT_URL)
            )
        )

    # Separate redirects to keep backwards compatibility with older
    # functions that don't expect a properties_list parameter
    if items_property_list:
        return HttpResponseRedirect(
            '%s?%s' % (
                action,
                urlencode(
                    {
                        'items_property_list': dumps(items_property_list),
                        'next': next
                    }
                )
            )
        )
    else:
        return HttpResponseRedirect('%s?%s' % (
            action,
            urlencode({'id_list': id_list, 'next': next}))
        )
