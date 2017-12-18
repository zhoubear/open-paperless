# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0008_auto_20150711_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformation',
            name='order',
            field=models.PositiveIntegerField(
                default=0, help_text='Order in which the transformations '
                'will be executed. If left unchanged, an automatic order '
                'value will be assigned.', db_index=True,
                verbose_name='Order', blank=True
            ),
            preserve_default=True,
        ),
    ]
