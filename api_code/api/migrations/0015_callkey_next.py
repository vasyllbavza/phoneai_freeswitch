# Generated by Django 3.2.7 on 2021-12-19 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_calllog_business_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='callkey',
            name='next',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next', to='api.callmenu'),
        ),
    ]
