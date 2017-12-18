# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_gpg', '0004_auto_20160322_2202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='key',
            name='key_id',
        ),
    ]
