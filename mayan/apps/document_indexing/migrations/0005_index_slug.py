# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_indexing', '0004_auto_20150708_0113'),
    ]

    operations = [
        migrations.AddField(
            model_name='index',
            name='slug',
            field=models.SlugField(
                null=True, max_length=128, blank=True, help_text='This values '
                'will be used by other apps to reference this index.',
                unique=True, verbose_name='Slug'
            ),
            preserve_default=True,
        ),
    ]
