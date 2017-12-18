# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20150706_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocaleprofile',
            name='language',
            field=models.CharField(
                max_length=8, verbose_name='Language', choices=[
                    ('ar', 'Arabic'), ('bg', 'Bulgarian'),
                    ('bs', 'Bosnian (Bosnia and Herzegovina)'),
                    ('da', 'Danish'), ('de', 'German (Germany)'),
                    ('en', 'English'), ('es', 'Spanish'), ('fa', 'Persian'),
                    ('fr', 'French'), ('hu', 'Hungarian'), ('hr', 'Croatian'),
                    ('id', 'Indonesian'), ('it', 'Italian'),
                    ('nl', 'Dutch (Netherlands)'), ('pl', 'Polish'),
                    ('pt', 'Portuguese'), ('pt-br', 'Portuguese (Brazil)'),
                    ('ro', 'Romanian (Romania)'), ('ru', 'Russian'),
                    ('sl', 'Slovenian'), ('tr', 'Turkish'),
                    ('vi', 'Vietnamese (Viet Nam)'),
                    ('zh-cn', 'Chinese (China)')
                ]
            ),
        ),
    ]
