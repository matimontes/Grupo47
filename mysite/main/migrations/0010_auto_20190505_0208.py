# Generated by Django 2.2.1 on 2019-05-05 05:08

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_subasta_inicio_de_subasta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotsale',
            name='dia_inicial',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='subasta',
            name='dia_inicial',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='subasta',
            name='inicio_de_subasta',
            field=models.DateField(),
        ),
    ]