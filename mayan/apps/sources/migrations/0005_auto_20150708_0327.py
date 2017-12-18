# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0004_auto_20150616_1931'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='source',
            options={
                'ordering': ('label',), 'verbose_name': 'Source',
                'verbose_name_plural': 'Sources'
            },
        ),
        migrations.RenameField(
            model_name='source',
            old_name='title',
            new_name='label',
        ),
    ]
