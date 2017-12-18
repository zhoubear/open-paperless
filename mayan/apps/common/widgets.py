from __future__ import unicode_literals

from django import forms
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class DetailSelectMultiple(forms.widgets.SelectMultiple):
    def __init__(self, queryset=None, *args, **kwargs):
        self.queryset = queryset
        super(DetailSelectMultiple, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=(), *args, **kwargs):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        css_class = final_attrs.get('class', 'list')
        output = '<ul class="%s">' % css_class
        options = None
        if value:
            if getattr(value, '__iter__', None):
                options = [(index, string) for index, string in
                           self.choices if index in value]
            else:
                options = [(index, string) for index, string in
                           self.choices if index == value]
        else:
            if self.choices:
                if self.choices[0] != ('', '---------') and value != []:
                    options = [(index, string) for index, string in
                               self.choices]

        if options:
            for index, string in options:
                if self.queryset:
                    try:
                        output += '<li><a href="%s">%s</a></li>' % (
                            self.queryset.get(pk=index).get_absolute_url(),
                            string)
                    except AttributeError:
                        output += '<li>%s</li>' % (string)
                else:
                    output += '<li>%s</li>' % string
        else:
            output += '<li>%s</li>' % _('None')
        return mark_safe(output + '</ul>\n')


class DisableableSelectWidget(forms.SelectMultiple):
    allow_multiple_selected = True

    def __init__(self, *args, **kwargs):
        self.disabled_choices = kwargs.pop('disabled_choices', ())
        super(DisableableSelectWidget, self).__init__(*args, **kwargs)

    def render_option(self, selected_choices, option_value, option_label):
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        if option_value in self.disabled_choices:
            disabled_html = u' disabled="disabled"'
        else:
            disabled_html = ''
        return format_html('<option value="{0}"{1}{2}>{3}</option>',
                           option_value,
                           selected_html,
                           disabled_html,
                           force_text(option_label))


# From: http://www.peterbe.com/plog/emailinput-html5-django
class EmailInput(forms.widgets.Input):
    """
    Class for a login form widget that accepts only well formated
    email address
    """
    input_type = 'email'

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update(dict(autocorrect='off',
                          autocapitalize='off',
                          spellcheck='false'))
        return super(EmailInput, self).render(name, value, attrs=attrs)


class PlainWidget(forms.widgets.Widget):
    """
    Class to define a form widget that effectively nulls the htmls of a
    widget and reduces the output to only it's value
    """
    def render(self, name, value, attrs=None):
        return mark_safe('%s' % value)


class TextAreaDiv(forms.widgets.Widget):
    """
    Class to define a form widget that simulates the behavior of a
    Textarea widget but using a div tag instead
    """

    def __init__(self, attrs=None):
        # The 'rows' and 'cols' attributes are required for HTML correctness.
        default_attrs = {'class': 'text_area_div'}
        if attrs:
            default_attrs.update(attrs)
        super(TextAreaDiv, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        flat_attrs = flatatt(self.build_attrs(attrs, name=name))
        content = conditional_escape(force_text(value))
        result = '<pre%s>%s</pre>' % (flat_attrs, content)
        return mark_safe(result)


def two_state_template(state, ok_icon='fa fa-check', fail_icon='fa fa-times'):
    if state:
        return mark_safe('<i class="text-success {}"></i>'.format(ok_icon))
    else:
        return mark_safe('<i class="text-danger {}"></i>'.format(fail_icon))
