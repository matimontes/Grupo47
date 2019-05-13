# Generated by Django 2.2.1 on 2019-05-05 01:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20190504_2152'),
    ]

    operations = [
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='fotos/%residencia.id)')),
                ('residencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='main.Residencia')),
            ],
        ),
    ]