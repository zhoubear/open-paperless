# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_signatures', '0004_auto_20160325_0418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentversionsignature',
            name='document_version',
        ),
        migrations.DeleteModel(
            name='DocumentVersionSignature',
        ),
    ]
