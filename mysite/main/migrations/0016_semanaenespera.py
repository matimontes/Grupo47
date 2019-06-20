# Generated by Django 2.2.1 on 2019-06-20 02:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20190619_2143'),
    ]

    operations = [
        migrations.CreateModel(
            name='SemanaEnEspera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_inicial', models.DateField()),
                ('precio_reserva', models.DecimalField(decimal_places=2, max_digits=11)),
                ('residencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semanas_en_espera', to='main.Residencia')),
            ],
            options={
                'ordering': ['dia_inicial', 'residencia'],
                'abstract': False,
            },
        ),
    ]
