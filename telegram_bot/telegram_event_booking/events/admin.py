from django.contrib import admin
from events.models import Event, Ticket

# Display booking history in Ticket Admin
class TicketAdmin(admin.ModelAdmin):
    list_display = ("user_name", "ticket_id", "event", "created_at")  # Fields to display
    search_fields = ("user_name", "ticket_id", "event__name")         # Add search functionality
    list_filter = ("event", "created_at")                            # Add filtering options

# Register models in admin
admin.site.register(Event)
admin.site.register(Ticket, TicketAdmin)
