import os
import sys
import django
from asgiref.sync import sync_to_async

# Add the project directory to the Python path
sys.path.append('C:\\Users\\Huma\\OneDrive\\Desktop\\telegram bot\\telegram_event_booking')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_booking.settings')

# Set up Django environment
django.setup()

from events.models import Event

async def test_sync_to_async():
    events = await sync_to_async(list)(Event.objects.all())
    for event in events:
        print(f"Event: {event.name}")

# Run the async test function
import asyncio
asyncio.run(test_sync_to_async())
