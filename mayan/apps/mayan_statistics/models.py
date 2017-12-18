from __future__ import unicode_literals

import json

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class StatisticResult(models.Model):
    # Translators: 'Slug' refers to the URL valid ID of the statistic
    # More info: https://docs.djangoproject.com/en/1.7/glossary/#term-slug
    slug = models.SlugField(verbose_name=_('Slug'))
    datetime = models.DateTimeField(
        auto_now=True, verbose_name=_('Date time')
    )
    serialize_data = models.TextField(blank=True, verbose_name=_('Data'))

    def get_data(self):
        return json.loads(self.serialize_data)

    def store_data(self, data):
        self.serialize_data = json.dumps(data)
        self.save()

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = _('Statistics result')
        verbose_name_plural = _('Statistics results')
