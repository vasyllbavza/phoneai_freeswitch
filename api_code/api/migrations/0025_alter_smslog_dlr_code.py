# Generated by Django 3.2.7 on 2022-03-08 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_auto_20220308_0253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smslog',
            name='dlr_code',
            field=models.IntegerField(default=0, help_text='https://support.flowroute.com/681766-Delivery-Receipt-Response-Codes'),
        ),
    ]
