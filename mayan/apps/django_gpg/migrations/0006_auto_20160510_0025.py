# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gpg', '0005_remove_key_key_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='key_data',
            field=models.TextField(
                help_text='ASCII armored version of the key.',
                verbose_name='Key data'
            ),
        ),
    ]
