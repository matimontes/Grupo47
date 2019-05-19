# Generated by Django 2.2.1 on 2019-05-19 03:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20190518_2343'),
    ]

    operations = [
        migrations.AddField(
            model_name='subasta',
            name='usuarios_inscriptos',
            field=models.ManyToManyField(related_name='inscripciones', to='main.Usuario'),
        ),
        migrations.AlterField(
            model_name='puja',
            name='subasta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pujas', to='main.Subasta'),
        ),
        migrations.DeleteModel(
            name='SubastaEvento',
        ),
    ]
