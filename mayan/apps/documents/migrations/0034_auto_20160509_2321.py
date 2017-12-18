# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0033_auto_20160325_0052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='in_trash',
            field=models.BooleanField(default=False, verbose_name='In trash?', db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name='document',
            name='is_stub',
            field=models.BooleanField(default=True, editable=False, help_text='A document stub is a document with an entry on the database but no file uploaded. This could be an interrupted upload or a deferred upload via the API.', verbose_name='Is stub?', db_index=True),
        ),
    ]
