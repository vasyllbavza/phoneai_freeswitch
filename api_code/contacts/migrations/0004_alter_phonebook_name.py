# Generated by Django 3.2.7 on 2022-06-27 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_auto_20220627_0539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonebook',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Phonebook Nmae'),
        ),
    ]
