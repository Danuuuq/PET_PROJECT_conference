# Generated by Django 5.1.4 on 2025-01-07 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audioconf', '0010_remove_bookingacs_время_начала_бронирование_в_прошлом'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название подразделения'),
        ),
    ]
