# event_booking/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),  # Include the admin URLs
    path('', include('events.urls')),  # Include the events app URLs
    path('jet/', include('jet.urls', namespace='jet')), #django-jet for morden admin panel
]
