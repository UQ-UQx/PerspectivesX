# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-19 04:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perspectivesx', '0002_remove_template_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='item_terminology',
            field=models.CharField(default='item', max_length=1000, verbose_name='Item Terminology'),
        ),
        migrations.AddField(
            model_name='activity',
            name='perspective_terminology',
            field=models.CharField(default='perspective', max_length=1000, verbose_name='Perspective Terminology'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='perspective_selection',
            field=models.CharField(choices=[('Allow learners to choose a perspective', 'Allow learners to choose a perspective'), ('Randomly assign a perspective for learner', 'Randomly assign a perspective for learner'), ('Allow Learners to contribute to all perspectives', 'Allow Learners to contribute to all perspectives')], default='Randomly assign a perspective for learner', max_length=100),
        ),
    ]
