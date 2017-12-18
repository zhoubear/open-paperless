# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0002_auto_20150628_0533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='name',
        ),
    ]
