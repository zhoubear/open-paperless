# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_indexing', '0008_auto_20150729_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indextemplatenode',
            name='expression',
            field=models.CharField(
                help_text="Enter a template to render. Use Django's default "
                "templating language (https://docs.djangoproject.com/en/1.7/"
                "ref/templates/builtins/)", max_length=128,
                verbose_name='Indexing expression'
            ),
            preserve_default=True,
        ),
    ]
