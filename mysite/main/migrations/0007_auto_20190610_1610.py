# Generated by Django 2.2.1 on 2019-06-10 19:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20190610_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='fecha de nacimiento'),
        ),
    ]