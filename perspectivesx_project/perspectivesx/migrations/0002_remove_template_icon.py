# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-13 12:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perspectivesx', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='icon',
        ),
    ]
