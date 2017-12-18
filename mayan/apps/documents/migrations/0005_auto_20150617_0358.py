# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_auto_20150616_1930'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentpage',
            old_name='content',
            new_name='content_old',
        ),
    ]
