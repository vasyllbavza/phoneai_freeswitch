# Generated by Django 3.2.7 on 2021-11-16 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent', models.IntegerField(blank=True, max_length=11, null=True)),
                ('keys', models.CharField(blank=True, max_length=5, null=True)),
                ('level', models.IntegerField(default=0)),
                ('processed', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.calllog')),
            ],
            options={
                'verbose_name': 'CallKey',
                'verbose_name_plural': 'CallKeys',
                'db_table': 'call_keys',
                'managed': True,
            },
        ),
    ]
