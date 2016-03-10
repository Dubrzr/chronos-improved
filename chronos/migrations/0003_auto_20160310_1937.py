# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-10 19:37
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chronos', '0002_auto_20160310_1645'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('api_id', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='room',
        ),
        migrations.AddField(
            model_name='lesson',
            name='rooms',
            field=models.ManyToManyField(to='chronos.Room'),
        ),
        migrations.AlterField(
            model_name='room',
            name='api_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='parent_api_id',
            field=models.IntegerField(default=0),
        ),
    ]