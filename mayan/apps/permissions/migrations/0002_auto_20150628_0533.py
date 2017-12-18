# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permissionholder',
            name='holder_type',
        ),
        migrations.RemoveField(
            model_name='permissionholder',
            name='permission',
        ),
        migrations.DeleteModel(
            name='PermissionHolder',
        ),
        migrations.RemoveField(
            model_name='rolemember',
            name='member_type',
        ),
        migrations.RemoveField(
            model_name='rolemember',
            name='role',
        ),
        migrations.DeleteModel(
            name='RoleMember',
        ),
        migrations.AddField(
            model_name='role',
            name='groups',
            field=models.ManyToManyField(
                related_name='roles', verbose_name='Groups', to='auth.Group'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(
                related_name='roles', verbose_name='Permissions',
                to='permissions.StoredPermission'
            ),
            preserve_default=True,
        ),
    ]
