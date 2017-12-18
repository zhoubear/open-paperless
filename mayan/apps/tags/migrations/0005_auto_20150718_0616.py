# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0004_auto_20150717_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorful.fields.RGBColorField(verbose_name='Color'),
            preserve_default=True,
        ),
    ]
