# Create your models here.
from django.db import models
import uuid

# Events models to display events details on webserver and on telegram bot
class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
# Tickets models to store ticket details and barcode images -- Telegram Bot
class Ticket(models.Model):
    user_id = models.CharField(max_length=255)  # Telegram user ID
    user_name = models.CharField(max_length=255)  # User's name
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Random unique ticket ID
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)  # Path to barcode image

    def __str__(self):
        return f"{self.user_name} - {self.event.name}"
