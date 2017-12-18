# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_remove_documentpage_content_old'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentpage',
            name='page_label',
        ),
    ]
