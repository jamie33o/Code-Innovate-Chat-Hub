# Generated by Django 3.2.21 on 2023-10-21 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20231020_2349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channelposts',
            name='image',
        ),
        migrations.AddField(
            model_name='channelposts',
            name='images',
            field=models.TextField(blank=True),
        ),
    ]