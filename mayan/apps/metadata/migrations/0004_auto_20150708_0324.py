# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0003_auto_20150708_0323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadatatype',
            name='label',
            field=models.CharField(max_length=48, verbose_name='Label'),
            preserve_default=True,
        ),
    ]
