# Generated by Django 3.2.7 on 2022-01-29 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_auto_20220117_0221'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonenumber',
            name='max_attempt',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='retry_auto',
            field=models.IntegerField(default=0),
        ),
    ]
