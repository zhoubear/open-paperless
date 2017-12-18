# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_search', '0002_auto_20150920_0202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recentsearch',
            name='user',
        ),
        migrations.DeleteModel(
            name='RecentSearch',
        ),
    ]
