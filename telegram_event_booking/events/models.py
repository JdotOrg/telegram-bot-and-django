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
    thumbnail = models.ImageField(upload_to='event_thumbnails/', null=True, blank=True)  # New field for thumbnail
    
    def __str__(self):
        return self.name
    
     # Display thumbnail in the admin panel
    def thumbnail_tag(self):
        if self.thumbnail:
            return f'<img src="{self.thumbnail.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />'
        return "No Image"

    thumbnail_tag.short_description = "Thumbnail"
    thumbnail_tag.allow_tags = True
    
# Tickets models to store ticket details and barcode images -- Telegram Bot
class Ticket(models.Model):
    user_id = models.CharField(max_length=255)  # Telegram user ID
    user_name = models.CharField(max_length=255)  # User's name
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Random unique ticket ID
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)  # Path to barcode image
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.event.name}"
