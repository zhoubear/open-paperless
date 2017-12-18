# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_auto_20150617_0358'),
        ('ocr', '0003_auto_20150617_0401'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentpage',
            name='content_old',
        ),
    ]
