# Generated by Django 2.2.1 on 2019-07-11 23:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_opinion'),
    ]

    operations = [
        migrations.AddField(
            model_name='opinion',
            name='descripcion',
            field=models.TextField(default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='opinion',
            name='puntaje',
            field=models.IntegerField(default=10, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)]),
        ),
    ]
