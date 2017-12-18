# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0023_auto_20150715_0259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentversion',
            name='comment',
            field=models.TextField(
                default='', verbose_name='Comment', blank=True
            ),
            preserve_default=True,
        ),
    ]
