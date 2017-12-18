from __future__ import unicode_literals

import datetime

from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from common.literals import TIME_DELTA_UNIT_CHOICES


class SplitTimeDeltaWidget(forms.widgets.MultiWidget):
    """
    A Widget that splits a timedelta input into three <input type="text">
    boxes.
    """

    def __init__(self, attrs=None):
        widgets = (
            forms.widgets.NumberInput(
                attrs={
                    'maxlength': 4, 'style': 'width: 8em;',
                    'placeholder': _('Period')
                }
            ),
            forms.widgets.Select(
                attrs={'style': 'width: 8em;'}, choices=TIME_DELTA_UNIT_CHOICES
            ),

        )
        super(SplitTimeDeltaWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        return (None, None)

    def value_from_datadict(self, querydict, files, name):
        unit = querydict.get('{}_1'.format(name))
        period = querydict.get('{}_0'.format(name))

        if not unit or not period:
            return now()

        period = int(period)

        timedelta = datetime.timedelta(**{unit: period})
        return now() + timedelta
