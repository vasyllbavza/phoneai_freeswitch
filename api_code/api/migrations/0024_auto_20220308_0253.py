# Generated by Django 3.2.7 on 2022-03-08 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_smslog'),
    ]

    operations = [
        migrations.AddField(
            model_name='smslog',
            name='dlr_code',
            field=models.IntegerField(default=0, verbose_name='https://support.flowroute.com/681766-Delivery-Receipt-Response-Codes'),
        ),
        migrations.AlterField(
            model_name='smslog',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Queue'), (2, 'Success'), (3, 'Failed')], default=0),
        ),
    ]
