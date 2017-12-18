# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0003_sourcelog'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sourcelog',
            options={
                'ordering': ('-datetime',), 'get_latest_by': 'datetime',
                'verbose_name': 'Log entry',
                'verbose_name_plural': 'Log entries'
            },
        ),
    ]
