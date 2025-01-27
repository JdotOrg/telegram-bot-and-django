# event_booking/urls.py
from django.contrib import admin
from django.urls import include, path
from django.conf import settings  # Import settings
from django.conf.urls.static import static  # Import static for media files

urlpatterns = [
    path('admin/', admin.site.urls),  # Include the admin URLs
    path('', include('events.urls')),  # Include the events app URLs
    path('jet/', include('jet.urls', namespace='jet')),
]

# Serve media files during development
if settings.DEBUG:  # Only serve media in DEBUG mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
