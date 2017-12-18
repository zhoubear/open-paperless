# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20150608_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='autoadminsingleton',
            name='account',
        ),
        migrations.DeleteModel(
            name='AutoAdminSingleton',
        ),
    ]
