# Generated by Django 2.2.1 on 2019-05-05 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20190504_2259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotsale',
            name='dia_final',
        ),
        migrations.RemoveField(
            model_name='subasta',
            name='dia_final',
        ),
    ]
