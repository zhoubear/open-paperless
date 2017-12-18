# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('checkouts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentcheckout',
            name='user',
            field=models.ForeignKey(
                verbose_name='User', blank=True, to=settings.AUTH_USER_MODEL,
                null=True
            ),
            preserve_default=True,
        ),
    ]
