# Generated by Django 5.1.4 on 2025-01-07 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audioconf', '0009_department_employees_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bookingacs',
            name='Время начала бронирование в прошлом',
        ),
    ]
