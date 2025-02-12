# Generated by Django 3.2.7 on 2022-03-12 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_smslog_callback_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingSMS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_from', models.CharField(max_length=20)),
                ('sms_to', models.CharField(max_length=20)),
                ('sms_body', models.CharField(max_length=140)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('sms_id', models.CharField(blank=True, max_length=100, null=True)),
                ('smslog', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.smslog')),
            ],
            options={
                'verbose_name': 'Incoming SMS Log',
                'verbose_name_plural': 'Incoming SMS Logs',
                'db_table': 'incoming_sms',
                'managed': True,
            },
        ),
    ]
