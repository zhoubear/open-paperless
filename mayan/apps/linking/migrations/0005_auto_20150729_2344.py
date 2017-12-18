# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linking', '0004_auto_20150708_0320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartlink',
            name='dynamic_label',
            field=models.CharField(
                help_text="Enter a template to render. Use Django's default "
                "templating language (https://docs.djangoproject.com/en/1.7/"
                "ref/templates/builtins/). The {{ document }} context "
                "variable is available.", max_length=96,
                verbose_name='Dynamic label', blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='smartlinkcondition',
            name='expression',
            field=models.TextField(
                help_text="Enter a template to render. Use Django's default "
                "templating language (https://docs.djangoproject.com/en/1.7/"
                "ref/templates/builtins/). The {{ document }} context "
                "variable is available.", verbose_name='Expression'
            ),
            preserve_default=True,
        ),
    ]
