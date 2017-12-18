# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linking', '0003_auto_20150708_0318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartlink',
            name='dynamic_label',
            field=models.CharField(
                help_text='This expression will be evaluated against the '
                'current selected document.', max_length=96,
                verbose_name='Dynamic label', blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='smartlink',
            name='label',
            field=models.CharField(max_length=96, verbose_name='Label'),
            preserve_default=True,
        ),
    ]
