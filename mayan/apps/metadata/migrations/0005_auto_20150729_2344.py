# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0004_auto_20150708_0324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadatatype',
            name='default',
            field=models.CharField(
                help_text="Enter a template to render. Use Django's default "
                "templating language (https://docs.djangoproject.com/en/1.7/"
                "ref/templates/builtins/)", max_length=128, null=True,
                verbose_name='Default', blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='metadatatype',
            name='lookup',
            field=models.TextField(
                help_text="Enter a template to render. Must result in a "
                "comma delimited string. Use Django's default templating "
                "language (https://docs.djangoproject.com/en/1.7/ref/"
                "templates/builtins/).", null=True, verbose_name='Lookup',
                blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='metadatatype',
            name='name',
            field=models.CharField(
                help_text='Name used by other apps to reference this value. '
                'Do not use python reserved words, or spaces.', unique=True,
                max_length=48, verbose_name='Name'
            ),
            preserve_default=True,
        ),
    ]
