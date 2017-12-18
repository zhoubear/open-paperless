# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='submit_date',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='Date time submitted',
                db_index=True
            ),
            preserve_default=True,
        ),
    ]
