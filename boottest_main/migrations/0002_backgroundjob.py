# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boottest_main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackgroundJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('method', models.CharField(max_length=50, verbose_name='Method')),
                ('args', models.CharField(blank=True, max_length=200, default='', verbose_name='Args')),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('job_id', models.CharField(blank=True, max_length=100, default='', verbose_name='Job ID')),
                ('result', models.CharField(blank=True, max_length=200, default='', verbose_name='Result')),
                ('end_time', models.DateTimeField(blank=True, default=None, verbose_name='End Time', null=True)),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
    ]
