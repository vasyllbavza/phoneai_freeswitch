# Generated by Django 3.2.7 on 2021-12-10 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_calllog_attempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='callmenu',
            name='route_keys',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
