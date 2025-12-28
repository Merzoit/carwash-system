import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site1.settings')
import django
django.setup()

from carwash.models import Pay

pays = Pay.objects.all()
for pay in pays:
    name_lower = pay.name.lower()
    print(f'ID {pay.id}: {pay.name}')
    print(f'наличн in name: {"наличн" in name_lower}')
    print(f'карт in name: {"карт" in name_lower}')
    print(f'онлайн in name: {"онлайн" in name_lower}')
    print()


