# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0005_auto_20150708_0327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='label',
            field=models.CharField(max_length=64, verbose_name='Label'),
            preserve_default=True,
        ),
    ]
