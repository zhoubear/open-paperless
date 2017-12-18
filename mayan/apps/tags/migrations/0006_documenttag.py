# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0005_auto_20150718_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTag',
            fields=[
            ],
            options={
                'verbose_name': 'Document tag',
                'proxy': True,
                'verbose_name_plural': 'Document tags',
            },
            bases=('tags.tag',),
        ),
    ]
