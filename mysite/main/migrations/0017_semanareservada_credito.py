# Generated by Django 2.2.1 on 2019-07-11 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_semanaenespera'),
    ]

    operations = [
        migrations.AddField(
            model_name='semanareservada',
            name='credito',
            field=models.BooleanField(default=True),
        ),
    ]
