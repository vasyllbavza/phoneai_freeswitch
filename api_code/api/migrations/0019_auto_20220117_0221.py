# Generated by Django 3.2.7 on 2022-01-17 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_callkey_next'),
    ]

    operations = [
        migrations.AddField(
            model_name='callmenu',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
