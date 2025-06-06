import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from audioconf.models import AcsPhone, Department


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов в базу данных'

    def handle(self, *args, **kwargs):

        data_dir = settings.BASE_DIR / 'data'

        self.import_data(data_dir / 'acs_phone.csv',
                         AcsPhone)

    def import_data(self, file_path, model):
        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            data = [model(acs_id=row[0], phone=row[1],
                          password=row[2],
                          department=Department.objects.get(id=row[3]))
                    for row in reader]
            model.objects.bulk_create(data)
        self.stdout.write(self.style.SUCCESS('Успешная загрузка '
                                             f'данных из {file_path}'))
