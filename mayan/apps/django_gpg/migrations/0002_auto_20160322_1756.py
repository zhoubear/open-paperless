# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gpg', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='key',
            name='data',
        ),
        migrations.AddField(
            model_name='key',
            name='key_data',
            field=models.TextField(default='', verbose_name='Key data'),
            preserve_default=False,
        ),
    ]
