# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_delete_anonymoususersingleton'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shareduploadedfile',
            old_name='datatime',
            new_name='datetime',
        ),
    ]
