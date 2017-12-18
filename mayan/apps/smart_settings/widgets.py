from __future__ import unicode_literals

from django.utils.safestring import mark_safe


def setting_widget(instance):
    return mark_safe(
        '''
            <strong>{}</strong>
            <p class="small">{}</p>
        '''.format(instance, instance.help_text or '')
    )
