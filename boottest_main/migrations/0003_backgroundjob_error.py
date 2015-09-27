# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boottest_main', '0002_backgroundjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='backgroundjob',
            name='error',
            field=models.TextField(blank=True, default='', verbose_name='Error'),
        ),
    ]
