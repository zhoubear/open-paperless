# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_signatures', '0005_auto_20160325_0748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signaturebasemodel',
            name='public_key_fingerprint',
            field=models.CharField(
                verbose_name='Public key fingerprint', max_length=40,
                null=True, editable=False, blank=True
            ),
        ),
    ]
