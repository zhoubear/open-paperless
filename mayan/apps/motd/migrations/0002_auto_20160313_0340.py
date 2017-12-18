# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motd', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageoftheday',
            name='end_datetime',
            field=models.DateTimeField(
                null=True, verbose_name='End date time', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='messageoftheday',
            name='start_datetime',
            field=models.DateTimeField(
                null=True, verbose_name='Start date time', blank=True
            ),
        ),
    ]
