import datetime as dt 

from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class BookingQuerySet(models.QuerySet):
    def with_related_data(self):
        return self.select_related('acs_phone', 'owner')


class AcsQuerySet(models.QuerySet):
    def with_related_data(self):
        return self.prefetch_related('bookings', 'department',
                                     'department__employees')


class Department(models.Model):
    name = models.CharField('Название подразделения',
                            max_length=100, unique=True)
    is_superdepartment = models.BooleanField('Суперподразделение',
                                             default=False)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        default_related_name = 'departments'
        ordering = ('id', 'name',)

    def __str__(self):
        return f'{self.name}'


class Employees(models.Model):
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    middle_name = models.CharField('Отчество', max_length=50, blank=True)
    email = models.EmailField('Email', unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                   default=None, null=True, blank=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        default_related_name = 'employees'
        ordering = ('last_name', 'first_name', 'middle_name',)

    def __str__(self):
        name = (self.last_name + ' ' + self.first_name[0]
                + '.' + self.middle_name[0] + '.')
        return f'{name}'


class AcsPhone(models.Model):
    acs_id = models.IntegerField('ID конференции', unique=True,
                                 help_text='ID конференции на АКСС')
    phone = models.IntegerField('Номер конференции', unique=True,
                                blank=False, null=False, validators=[
                                    MinValueValidator(33300),
                                    MaxValueValidator(33399)],
                                help_text='5-значный внутренний номер')
    password = models.IntegerField('ПИН-код конференции', blank=False,
                                   null=False, validators=[
                                       MinValueValidator(0000),
                                       MaxValueValidator(9999)],
                                   help_text='ПИН-код от номера на АКСС')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                   default=1, null=True, blank=True)

    objects = AcsQuerySet.as_manager()

    class Meta:
        verbose_name = 'АКС Номер'
        verbose_name_plural = 'АКС Номера'
        default_related_name = 'acs_phones'
        ordering = ('phone', 'acs_id',)
        constraints = [
            models.UniqueConstraint(
                fields=('acs_id', 'phone'),
                name='Ограничение по уникальному номеру АКС'
            )
        ]

    def __str__(self):
        return f'{self.phone}'


class BookingAcs(models.Model):
    acs_phone = models.ForeignKey(AcsPhone, on_delete=models.CASCADE,
                                  verbose_name='АКС Номер')
    start_conf = models.DateTimeField('Время начала конференции')
    end_conf = models.DateTimeField('Время окончания конференции')
    responsible = models.TextField('Ответственный за бронирование',
                                   max_length=50, null=True, blank=True)
    owner = models.ForeignKey(User, verbose_name='Владелец бронирования',
                              on_delete=models.CASCADE)
    record = models.BooleanField(verbose_name='Предоставить запись',
                                 default=False)

    objects = BookingQuerySet.as_manager()

    class Meta:
        default_related_name = 'bookings'
        verbose_name = 'Бронь АКС номера'
        verbose_name_plural = 'Бронирования АКС номеров'
        ordering = ('start_conf', 'end_conf', 'acs_phone')
        constraints = [
            models.CheckConstraint(
                condition=Q(start_conf__lt=F('end_conf')),
                name='Время начало бронирования после времени окончания'
            ),
            # При миграции выдает ошибку, так как существуют записи в прошлом
            # models.CheckConstraint(
            #     condition=Q(start_conf__gt=dt.datetime.now()),
            #     name='Время начала бронирование в прошлом'
            # ),
            models.CheckConstraint(
                condition=Q(start_conf__date=F('end_conf__date')),
                name='Бронирование заканчивается в следующий день'
            ),
        ]

    def clean(self):
        """Проверка на пересечение с другими бронированиями."""
        if self.start_conf and self.end_conf:
            overlapping_bookings = BookingAcs.objects.filter(
                acs_phone=self.acs_phone,
                start_conf__lt=self.end_conf,
                end_conf__gt=self.start_conf
            ).exclude(id=self.id)

            if overlapping_bookings.exists():
                raise ValidationError(
                    'Бронирование пересекается с уже существующими.')

    def __str__(self):
        return f'Бронь {self.responsible} номера {self.acs_phone} id {self.id}'
