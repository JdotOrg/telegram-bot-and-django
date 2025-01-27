import csv
from datetime import date
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from events.models import Event, Ticket


# Custom Action to Export as CSV
def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="exported_data.csv"'
    writer = csv.writer(response)

    # Add headers based on the model being exported
    if modeladmin.model == Event:
        writer.writerow(["Name", "Start Date", "End Date", "Location", "Description"])
        for event in queryset:
            writer.writerow([event.name, event.start_date, event.end_date, event.location, event.description])
    elif modeladmin.model == Ticket:
        writer.writerow(["User Name", "Ticket ID", "Event", "Created At"])
        for ticket in queryset:
            writer.writerow([ticket.user_name, ticket.ticket_id, ticket.event.name, ticket.created_at])

    return response


export_as_csv.short_description = "Export Selected as CSV"


# Custom Filter for Ongoing Events
class OngoingEventFilter(SimpleListFilter):
    title = "Event Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("ongoing", "Ongoing"),
            ("upcoming", "Upcoming"),
            ("past", "Past"),
        )

    def queryset(self, request, queryset):
        today = date.today()
        if self.value() == "ongoing":
            return queryset.filter(start_date__lte=today, end_date__gte=today)
        if self.value() == "upcoming":
            return queryset.filter(start_date__gt=today)
        if self.value() == "past":
            return queryset.filter(end_date__lt=today)
        return queryset


# Event Admin with Thumbnail, Actions, and Filters
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "location",
        "thumbnail_tag",
        "edit_button",
        "delete_button",
    )
    search_fields = ("name", "location")
    list_filter = ("start_date", "end_date", "location", OngoingEventFilter)
    actions = [export_as_csv]

    # Display thumbnail
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.thumbnail.url,
            )
        return "No Image"

    thumbnail_tag.short_description = "Thumbnail"

    # Add custom buttons for edit and delete actions
    def edit_button(self, obj):
        return format_html(
            '<a class="button" style="color: green;" href="/admin/events/event/{}/change/">Edit</a>',
            obj.id,
        )

    edit_button.short_description = "Edit"

    def delete_button(self, obj):
        return format_html(
            '<a class="button" style="color: red;" href="/admin/events/event/{}/delete/">Delete</a>',
            obj.id,
        )

    delete_button.short_description = "Delete"

    # Allow preview of the thumbnail in the detail view
    readonly_fields = ("thumbnail_tag",)


# Ticket Admin with CSV Export
class TicketAdmin(admin.ModelAdmin):
    list_display = ("user_name", "ticket_id", "event", "created_at")
    search_fields = ("user_name", "ticket_id", "event__name")
    list_filter = ("event", "created_at")
    actions = [export_as_csv]


# Custom Admin Titles
admin.site.site_header = "Event Management Admin"
admin.site.site_title = "Event Admin Portal"
admin.site.index_title = "Welcome to the Event Management Dashboard"

# Register models in admin
admin.site.register(Event, EventAdmin)
admin.site.register(Ticket, TicketAdmin)
