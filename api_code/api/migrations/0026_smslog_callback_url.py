# Generated by Django 3.2.7 on 2022-03-12 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_alter_smslog_dlr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='smslog',
            name='callback_url',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
