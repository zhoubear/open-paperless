from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import ungettext, ugettext_lazy as _

from common.views import (
    AssignRemoveView, MultipleObjectConfirmActionView,
    MultipleObjectFormActionView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectEditView, SingleObjectListView
)

from .forms import PasswordForm, UserForm
from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)


class GroupCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create new group')}
    fields = ('name',)
    model = Group
    post_action_redirect = reverse_lazy('user_management:group_list')
    view_permission = permission_group_create


class GroupEditView(SingleObjectEditView):
    fields = ('name',)
    model = Group
    post_action_redirect = reverse_lazy('user_management:group_list')
    view_permission = permission_group_edit

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit group: %s') % self.get_object(),
        }


class GroupListView(SingleObjectListView):
    extra_context = {
        'hide_link': True,
        'title': _('Groups'),
    }
    model = Group
    view_permission = permission_group_view


class GroupDeleteView(SingleObjectDeleteView):
    model = Group
    post_action_redirect = reverse_lazy('user_management:group_list')
    view_permission = permission_group_delete

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Delete the group: %s?') % self.get_object(),
        }


class GroupMembersView(AssignRemoveView):
    decode_content_type = True
    left_list_title = _('Available users')
    right_list_title = _('Members of groups')
    view_permission = permission_group_edit

    @staticmethod
    def generate_choices(choices):
        results = []
        for choice in choices:
            ct = ContentType.objects.get_for_model(choice)
            label = choice.get_full_name() if choice.get_full_name() else choice

            results.append(('%s,%s' % (ct.model, choice.pk), '%s' % (label)))

        # Sort results by the label not the key value
        return sorted(results, key=lambda x: x[1])

    def add(self, item):
        self.get_object().user_set.add(item)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Members of group: %s') % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(Group, pk=self.kwargs['pk'])

    def left_list(self):
        return GroupMembersView.generate_choices(
            get_user_model().objects.exclude(
                groups=self.get_object()
            ).exclude(is_staff=True).exclude(is_superuser=True)
        )

    def right_list(self):
        return GroupMembersView.generate_choices(
            self.get_object().user_set.all()
        )

    def remove(self, item):
        self.get_object().user_set.remove(item)


class UserCreateView(SingleObjectCreateView):
    extra_context = {
        'title': _('Create new user'),
    }
    form_class = UserForm
    view_permission = permission_user_create

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_unusable_password()
        user.save()
        messages.success(
            self.request, _('User "%s" created successfully.') % user
        )
        return HttpResponseRedirect(
            reverse('user_management:user_set_password', args=(user.pk,))
        )


class UserDeleteView(MultipleObjectConfirmActionView):
    model = get_user_model()
    success_message = _('User delete request performed on %(count)d user')
    success_message_plural = _(
        'User delete request performed on %(count)d users'
    )
    view_permission = permission_user_delete

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'title': ungettext(
                'Delete user',
                'Delete users',
                queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Delete user: %s') % queryset.first()
                }
            )

        return result

    def object_action(self, form, instance):
        try:
            if instance.is_superuser or instance.is_staff:
                messages.error(
                    self.request,
                    _(
                        'Super user and staff user deleting is not '
                        'allowed, use the admin interface for these cases.'
                    )
                )
            else:
                instance.delete()
                messages.success(
                    self.request, _(
                        'User "%s" deleted successfully.'
                    ) % instance
                )
        except Exception as exception:
            messages.error(
                self.request, _(
                    'Error deleting user "%(user)s": %(error)s'
                ) % {'user': instance, 'error': exception}
            )


class UserEditView(SingleObjectEditView):
    fields = ('username', 'first_name', 'last_name', 'email', 'is_active',)
    post_action_redirect = reverse_lazy('user_management:user_list')
    queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )
    view_permission = permission_user_edit

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit user: %s') % self.get_object(),
        }


class UserGroupsView(AssignRemoveView):
    decode_content_type = True
    left_list_title = _('Available groups')
    right_list_title = _('Groups joined')
    view_permission = permission_user_edit

    def add(self, item):
        item.user_set.add(self.get_object())

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Groups of user: %s') % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

    def left_list(self):
        return AssignRemoveView.generate_choices(
            Group.objects.exclude(user=self.get_object())
        )

    def right_list(self):
        return AssignRemoveView.generate_choices(
            Group.objects.filter(user=self.get_object())
        )

    def remove(self, item):
        item.user_set.remove(self.get_object())


class UserListView(SingleObjectListView):
    view_permission = permission_user_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'title': _('Users'),
        }

    def get_object_list(self):
        return get_user_model().objects.exclude(
            is_superuser=True
        ).exclude(is_staff=True).order_by('last_name', 'first_name')


class UserSetPasswordView(MultipleObjectFormActionView):
    form_class = PasswordForm
    model = get_user_model()
    success_message = _('Password change request performed on %(count)d user')
    success_message_plural = _(
        'Password change request performed on %(count)d users'
    )
    view_permission = permission_user_edit

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'submit_label': _('Submit'),
            'title': ungettext(
                'Change user password',
                'Change users passwords',
                queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Change password for user: %s') % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        queryset = self.get_queryset()
        result = {}
        if queryset:
            result['user'] = queryset.first()

        return result

    def object_action(self, form, instance):
        try:
            if instance.is_superuser or instance.is_staff:
                messages.error(
                    self.request,
                    _(
                        'Super user and staff user password '
                        'reseting is not allowed, use the admin '
                        'interface for these cases.'
                    )
                )
            else:
                instance.set_password(form.cleaned_data['new_password_1'])
                instance.save()
                messages.success(
                    self.request, _(
                        'Successfull password reset for user: %s.'
                    ) % instance
                )
        except Exception as exception:
            messages.error(
                self.request, _(
                    'Error reseting password for user "%(user)s": %(error)s'
                ) % {
                    'user': instance, 'error': exception
                }
            )
