# Generated by Django 3.2.7 on 2021-12-11 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_callmenu_route_keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='calllog',
            name='business_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
