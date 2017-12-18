# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motd', '0004_auto_20160314_0040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='end_datetime',
            field=models.DateTimeField(
                help_text='Date and time until when this message is to be '
                'displayed.', null=True, verbose_name='End date time',
                blank=True
            ),
        ),
        migrations.AlterField(
            model_name='message',
            name='label',
            field=models.CharField(
                help_text='Short description of this message.', max_length=32,
                verbose_name='Label'
            ),
        ),
        migrations.AlterField(
            model_name='message',
            name='message',
            field=models.TextField(
                help_text='The actual message to be displayed.',
                verbose_name='Message'
            ),
        ),
        migrations.AlterField(
            model_name='message',
            name='start_datetime',
            field=models.DateTimeField(
                help_text='Date and time after which this message will be '
                'displayed.', null=True, verbose_name='Start date time',
                blank=True
            ),
        ),
    ]
