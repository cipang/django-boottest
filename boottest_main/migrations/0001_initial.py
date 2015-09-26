# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestRecord',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('num_value', models.DecimalField(max_digits=6, decimal_places=3)),
                ('text_value', models.CharField(max_length=50)),
                ('created', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ('-num_value',),
            },
        ),
    ]
