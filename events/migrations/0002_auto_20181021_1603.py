# Generated by Django 2.1 on 2018-10-21 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='datetime',
        ),
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='event',
            name='time',
            field=models.TimeField(auto_now=True),
        ),
    ]
