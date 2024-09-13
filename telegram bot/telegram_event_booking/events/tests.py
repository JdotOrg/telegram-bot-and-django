from django.test import TestCase

# Create your tests here.
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_booking.settings')
django.setup()

print("Django setup successful.")
