# Generated by Django 2.2.1 on 2019-06-12 20:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20190610_1706'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='puja',
            options={'ordering': ['subasta', '-dinero_pujado']},
        ),
    ]