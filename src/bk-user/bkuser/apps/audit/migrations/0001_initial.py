# Generated by Django 3.2.25 on 2024-10-25 02:02

import bkuser.utils.uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OperationAuditRecord',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.CharField(blank=True, max_length=128, null=True)),
                ('updater', models.CharField(blank=True, max_length=128, null=True)),
                ('id', models.CharField(default=bkuser.utils.uuid.generate_uuid, max_length=128, primary_key=True, serialize=False)),
                ('event_id', models.CharField(default=bkuser.utils.uuid.generate_uuid, max_length=128, verbose_name='事件 ID')),
                ('tenant_id', models.CharField(max_length=128, verbose_name='租户 ID')),
                ('operation', models.CharField(max_length=64, verbose_name='操作行为')),
                ('object_type', models.CharField(max_length=32, verbose_name='操作对象类型')),
                ('object_id', models.CharField(max_length=128, verbose_name='操作对象 ID')),
                ('extras', models.JSONField(blank=True, null=True, verbose_name='额外信息')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
