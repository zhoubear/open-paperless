# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linking', '0002_resolvedsmartlink'),
    ]

    operations = [
        migrations.RenameField(
            model_name='smartlink',
            old_name='dynamic_title',
            new_name='dynamic_label',
        ),
        migrations.RenameField(
            model_name='smartlink',
            old_name='title',
            new_name='label',
        ),
    ]
