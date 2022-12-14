# Generated by Django 3.2.4 on 2021-07-28 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study_app', '0005_auto_20210720_0518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='chatRoomId',
        ),
        migrations.RemoveField(
            model_name='message',
            name='userId',
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='groupName',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.DeleteModel(
            name='ChatMember',
        ),
        migrations.DeleteModel(
            name='ChatRoom',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
