# Generated by Django 3.2.21 on 2023-10-24 23:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_auto_20231024_2355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channelmodel',
            name='posts_seen_by',
        ),
    ]
