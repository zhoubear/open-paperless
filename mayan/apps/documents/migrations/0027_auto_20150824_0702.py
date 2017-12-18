# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0026_auto_20150729_2140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttypefilename',
            options={
                'ordering': ('filename',),
                'verbose_name': 'Quick rename template',
                'verbose_name_plural': 'Quick rename templates'
            },
        ),
        migrations.AlterField(
            model_name='document',
            name='is_stub',
            field=models.BooleanField(
                default=True, help_text='A document stub is a document with '
                'an entry on the database but no file uploaded. This could '
                'be an interrupted upload or a deferred upload via the API.',
                verbose_name='Is stub?', editable=False
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documenttypefilename',
            name='filename',
            field=models.CharField(
                max_length=128, verbose_name='Label', db_index=True
            ),
            preserve_default=True,
        ),
    ]
