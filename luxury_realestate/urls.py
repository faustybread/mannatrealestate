"""
URL configuration for luxury_realestate project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')),
    path('', include('properties.urls', namespace='properties')),
]

# In DEBUG, serve user-uploaded media (property photos) via the dev server.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
