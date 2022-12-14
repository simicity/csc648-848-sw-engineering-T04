# Generated by Django 3.2.4 on 2021-07-20 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study_app', '0004_auto_20210715_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='memberCount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='studygroup',
            name='subject',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
