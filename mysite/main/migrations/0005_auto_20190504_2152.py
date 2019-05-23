# Generated by Django 2.2.1 on 2019-05-05 00:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20190504_2143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hotsale',
            old_name='diaFinal',
            new_name='dia_final',
        ),
        migrations.RenameField(
            model_name='hotsale',
            old_name='diaInicial',
            new_name='dia_inicial',
        ),
        migrations.RenameField(
            model_name='hotsale',
            old_name='precioReserva',
            new_name='precio_reserva',
        ),
        migrations.RenameField(
            model_name='subasta',
            old_name='diaFinal',
            new_name='dia_final',
        ),
        migrations.RenameField(
            model_name='subasta',
            old_name='diaInicial',
            new_name='dia_inicial',
        ),
        migrations.RenameField(
            model_name='subasta',
            old_name='precioInicial',
            new_name='precio_inicial',
        ),
        migrations.RenameField(
            model_name='subasta',
            old_name='precioReserva',
            new_name='precio_reserva',
        ),
        migrations.RemoveField(
            model_name='residencia',
            name='email',
        ),
    ]
