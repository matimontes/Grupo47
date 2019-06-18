# Generated by Django 2.2.1 on 2019-06-18 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20190612_1728'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Tarjeta',
        ),
        migrations.AlterField(
            model_name='user',
            name='creditos',
            field=models.IntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(verbose_name='fecha de nacimiento'),
        ),
        migrations.AlterField(
            model_name='user',
            name='nacionalidad',
            field=models.CharField(max_length=50),
        ),
    ]
