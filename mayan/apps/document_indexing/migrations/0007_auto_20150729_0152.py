# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_indexing', '0006_auto_20150729_0144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='index',
            name='slug',
            field=models.SlugField(
                default='', max_length=128, help_text='This values will be '
                'used by other apps to reference this index.', unique=True,
                verbose_name='Slug'
            ),
            preserve_default=False,
        ),
    ]
