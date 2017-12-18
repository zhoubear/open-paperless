# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0009_auto_20150930_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailbasemodel',
            name='store_body',
            field=models.BooleanField(default=True, help_text='Store the body of the email as a text document.', verbose_name='Store email body'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='imapemail',
            name='mailbox',
            field=models.CharField(default='INBOX', help_text='IMAP Mailbox from which to check for messages.', max_length=64, verbose_name='Mailbox'),
            preserve_default=True,
        ),
    ]
