import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site1.settings')
import django
django.setup()

from shared_algorythms import Math
from carwash.models import Shift

math_instance = Math()
shift = Shift.objects.last()
drop_balance = math_instance.shift_drop_balance(shift)

print('Drop balance:')
for key, value in drop_balance.items():
    print(f'  "{key}": {value}')
    print(f'    Lower: "{key.lower()}"')
    print(f'    аличн in lower: {"аличн" in key.lower()}')
    print(f'    арт in lower: {"арт" in key.lower()}')
    print(f'    нлайн in lower: {"нлайн" in key.lower()}')
    print()


